# -*- coding: utf-8 -*-

# (The MIT License)
#
# Copyright (c) 2013-2021 Kura
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Provides the Smtp protocol wrapper."""


import asyncio
import base64
import inspect
import logging
import random

from .protocols import StreamReaderProtocol
from .utils import message_id


__all__ = ("Smtp",)
"""Tuple all the things."""


logger = logging.getLogger("blackhole.smtp")


class Smtp(StreamReaderProtocol):
    """The class responsible for handling SMTP/SMTPS commands."""

    _bounce_responses = {
        450: "Requested mail action not taken: mailbox unavailable",
        451: "Requested action aborted: local error in processing",
        452: "Requested action not taken: insufficient system storage",
        458: "Unable to queue message",
        521: "Machine does not accept mail",
        550: "Requested action not taken: mailbox unavailable",
        551: "User not local",
        552: "Requested mail action aborted: exceeded storage allocation",
        553: "Requested action not taken: mailbox name not allowed",
        571: "Blocked",
    }
    """The response code and message for each bounce type."""

    _delay = None
    """The delay timer value."""

    _max_delay = 60
    """The maximum delay value in seconds. Cannot be more than 60 seconds."""

    _mode = None
    """The response mode to use."""

    _flags = {}
    """Flags defined in each listen directive."""

    _disable_dynamic_switching = False
    """
    This option disabled dynamic switching functionality.

    Dynamic switching will be disabled when mode= and delay= flags are
    configured.

    https://kura.gg/blackhole/configuration.html#listen
    https://kura.gg/blackhole/configuration.html#tls_listen
    """

    _failed_commands = 0
    """An internal counter of failed commands for a client."""

    def __init__(self, clients, loop=None):
        """
        Initialise the SMTP protocol.

        :param list clients: A list of connected clients.
        :param loop: The event loop to use.
        :type loop: :py:obj:`None` or
                    :py:class:`syncio.unix_events._UnixSelectorEventLoop`

        .. note::

           Loads the configuration, defines the server's FQDN and generates
           an RFC 2822 Message-ID.
        """
        super().__init__(clients, loop)
        self.message_id = message_id(self.fqdn)

    def connection_made(self, transport):
        """
        Tie a connection to blackhole to the SMTP protocol.

        :param asyncio.transports.Transport transport: The transport class.
        """
        super().connection_made(transport)
        logger.debug("Peer connected")
        self.transport = transport
        self.flags_from_transport()
        self.connection_closed = False
        self._handler_coroutine = self.loop.create_task(self._handle_client())

    async def push(self, code, msg):
        """
        Write a response code and message to the client.

        :param int code: SMTP code, i.e. 250.
        :param str msg: The message for the SMTP code
        """
        n_msg = f"{code} {msg}"
        await super().push(n_msg)

    async def _handle_client(self):
        """
        Handle a client connection.

        This method greets the client and then accepts and handles each line
        the client sends, passing off to the correct verb handler.
        """
        await self.greet()
        while not self.connection_closed:
            line = await self.wait()
            if line is None:
                await self.close()
                return
            logger.debug(f"RECV {line}")
            line = line.decode("utf-8").rstrip("\r\n")
            self._line = line
            handler = self.lookup_handler(line)
            if handler:
                await handler()
            else:
                await self.push(502, "5.5.2 Command not recognised")

    def get_auth_members(self):
        """
        Get a list of available AUTH mechanisms.

        :returns: A list of available authentication mechanisms.
        :rtype: :py:obj:`list`
        """
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        cmds = []
        for cmd, _ in members:
            if cmd.startswith("auth_") and cmd != "auth_UNKNOWN":
                cmd = cmd.replace("auth_", "").replace("_", "-")
                cmds.append(cmd)
        return cmds

    def lookup_auth_handler(self, line):
        """
        Look up a handler for the received AUTH mechanism.

        :param str line: A line of data from a client.
        :returns: A callable authentication mechanism.
        :rtype: `blackhole.smtp.Smtp.auth_MECHANISM`

        .. note::

           Using ``pass=`` as part of the auth data will trigger an
           authentication pass, using ``fail=`` will trigger an authentication
           failure.
        """
        parts = line.split(" ")
        if len(parts) < 2:
            return self.auth_UNKNOWN
        mechanism = parts[1].upper()
        if mechanism == "CRAM-MD5":
            return self.auth_CRAM_MD5
        if mechanism not in self.get_auth_members():
            return self.auth_UNKNOWN
        if len(parts) == 3 and mechanism == "PLAIN":
            if "fail=" in line:
                return self._auth_failure
            return self._auth_success
        return getattr(self, f"auth_{mechanism.upper()}", self.auth_UNKNOWN)

    async def auth_UNKNOWN(self):
        """Response to an unknown auth mechanism."""
        await self.push(501, "5.5.4 Syntax: AUTH mechanism")

    async def help_AUTH(self):
        """
        Send help for AUTH mechanisms.

        https://kura.gg/blackhole/communicating-with-blackhole.html#help
        """
        mechanisms = " ".join(self.get_auth_members())
        await self.push(250, f"Syntax: AUTH {mechanisms}")

    async def auth_LOGIN(self):
        """
        Handle an AUTH LOGIN request.

            >>> AUTH LOGIN
            334 VXNlcm5hbWU6
            >>> pass=letmein
            235 2.7.0 Authentication successful

            >>> AUTH LOGIN
            334 VXNlcm5hbWU6
            >>> fail=letmein
            535 5.7.8 Authentication failed

        .. note::

           Using ``pass=`` as part of the auth data will trigger an
           authentication pass, using ``fail=`` will trigger an authentication
           failure.
        """
        await self.push(334, "VXNlcm5hbWU6")
        line = await self.wait()
        logger.debug(f"RECV {line}")
        if b"fail=" in line.lower():
            await self._auth_failure()
        else:
            await self._auth_success()

    async def auth_CRAM_MD5(self):
        """
        Handle an AUTH CRAM-MD5 request.

            >>> AUTH CRAM-MD5
            334 PDE0NjE5MzA1OTYwMS4yMDQ5LjEyMzI4NTE2...
            >>> pass=letmein
            235 2.7.0 Authentication successful

            >>> AUTH CRAM-MD5
            334 PDE0NjE5MzA1OTYwMS4yMDQ5LjEyMzI4NTE2...
            >>> fail=letmein
            535 5.7.8 Authentication failed

        .. note::

           Using ``pass=`` as part of the auth data will trigger an
           authentication pass, using ``fail=`` will trigger an authentication
           failure.
        """
        emessage_id = base64.b64encode(self.message_id.encode("utf-8"), b"==")
        await self.push(334, emessage_id.decode("utf-8"))
        line = await self.wait()
        logger.debug(f"RECV {line}")
        if b"fail=" in line.lower():
            await self._auth_failure()
        else:
            await self._auth_success()

    async def auth_PLAIN(self):
        """Handle an AUTH PLAIN request.

            >>> AUTH PLAIN
            334
            >>> pass=letmein
            235 2.7.0 Authentication successful

            >>> AUTH PLAIN
            334
            >>> fail=letmein
            535 5.7.8 Authentication failed

            >>> AUTH PLAIN pass=letmein
            235 2.7.0 Authentication successful

            >>> AUTH PLAIN fail=letmein
            535 5.7.8 Authentication failed

        .. note::

           Using ``pass=`` as part of the auth data will trigger an
           authentication pass, using ``fail=`` will trigger an authentication
           failure.
        """
        await self.push(334, " ")
        line = await self.wait()
        logger.debug(f"RECV {line}")
        if b"fail=" in line.lower():
            await self._auth_failure()
        else:
            await self._auth_success()

    async def _auth_success(self):
        """Send an authentication successful response."""
        await self.push(235, "2.7.0 Authentication successful")

    async def _auth_failure(self):
        """Send an authentication failure response."""
        await self.push(535, "5.7.8 Authentication failed")

    async def timeout(self):
        """
        Timeout a client connection.

        Sends the 421 timeout message to the client and closes the connection.

        https://kura.gg/blackhole/configuration.html#timeout
        """
        logger.debug(
            f"Peer timed out, no data received for {self.config.timeout} "
            "seconds",
        )
        await self.push(421, "Timeout")
        await self.close()

    def lookup_handler(self, line):
        """
        Look up the SMTP VERB against a handler.

        :param str line: Look up the command handler to use from the data
                         provided.
        :returns: A callable command handler.
        :rtype: `blackhole.smtp.Smtp.do_VERB`,
                `blackhole.smtp.Smtp.auth_MECHANISM`,
                `blackhole.smtp.Smtp.help_VERB`
        """
        parts = line.split(None, 1)
        if parts:
            if parts[0].lower() == "help":
                return self.lookup_help_handler(parts)
            if parts[0].lower() == "auth":
                return self.lookup_auth_handler(line)
            else:
                return self.lookup_verb_handler(parts[0])
        return self.do_UNKNOWN

    def lookup_help_handler(self, parts):
        """
        Look up a help handler for the SMTP VERB.

        https://kura.gg/blackhole/communicating-with-blackhole.html#help

        :param list parts: A list of command data, split on spaces.
        :returns: A callable help handler.
        :rtype: `blackhole.smtp.Smtp.help_VERB`
        """
        if len(parts) > 1:
            cmd = f"help_{parts[1].upper()}"
        else:
            cmd = "do_HELP"
        return getattr(self, cmd, self.help_UNKNOWN)

    def lookup_verb_handler(self, verb):
        """
        Look up a handler for the SMTP VERB.

        :param str verb:
        :returns: A callable command handler.
        :rtype: `blackhole.smtp.Smtp.do_VERB`
        """
        return getattr(self, f"do_{verb.upper()}", self.do_UNKNOWN)

    async def greet(self):
        """Send a greeting to the client."""
        await self.push(220, f"{self.fqdn} ESMTP")

    def get_help_members(self):
        """
        Get a list of HELP handlers for verbs.

        https://kura.gg/blackhole/communicating-with-blackhole.html#help

        :returns: A list of available help handlers.
        :rtype: :py:obj:`list`
        """
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        cmds = []
        for cmd, _ in members:
            if cmd.startswith("help_") and not cmd == "help_UNKNOWN":
                cmds.append(cmd.replace("help_", ""))
        return cmds

    async def do_HELP(self):
        """
        Send a response to the HELP verb.

        https://kura.gg/blackhole/communicating-with-blackhole.html#help
        """
        msg = " ".join(self.get_help_members())
        await self.push(250, f"Supported commands: {msg}")

    async def help_HELO(self):
        """
        Send help for HELO verb.

        https://kura.gg/blackhole/communicating-with-blackhole.html#help
        """
        await self.push(250, "Syntax: HELO domain.tld")

    async def do_HELO(self):
        """Send response to HELO verb."""
        await self.push(250, "OK")

    async def help_EHLO(self):
        """
        Send help for the EHLO verb.

        https://kura.gg/blackhole/communicating-with-blackhole.html#help
        """
        await self.push(250, "Syntax: EHLO domain.tld")

    async def do_EHLO(self):
        """Send response to EHLO verb."""
        response = f"250-{self.fqdn}\r\n".encode("utf-8")
        self._writer.write(response)
        logger.debug(f"SENT {response}")
        auth = " ".join(self.get_auth_members())
        responses = (
            "250-HELP",
            "250-PIPELINING",
            f"250-AUTH {auth}",
            f"250-SIZE {self.config.max_message_size}",
            "250-VRFY",
            "250-ETRN",
            "250-ENHANCEDSTATUSCODES",
            "250-8BITMIME",
            "250-SMTPUTF8",
            "250-EXPN",
            "250 DSN",
        )
        for response in responses:
            response = f"{response}\r\n".encode("utf-8")
            logger.debug(f"SENT {response}")
            self._writer.write(response)
        await self._writer.drain()

    async def help_MAIL(self):
        """
        Send help for the MAIL TO verb.

        https://kura.gg/blackhole/communicating-with-blackhole.html#help
        """
        await self.push(250, "Syntax: MAIL FROM: <address>")

    async def _size_in_mail(self):
        """
        Handle ``SIZE=`` being passed in ``MAIL`` verb.

        Send a 552 response if the size provided is larger than
        max_message_size.
        """
        parts = self._line.lower().split(" ")
        size = None
        for part in parts:
            if part.startswith("size="):
                size = part.split("=")[1]
        if (
            size is not None
            and size.isdigit()
            and int(size) > self.config.max_message_size
        ):
            await self.push(
                552,
                "Message size exceeds fixed maximum message size",
            )
        else:
            await self.push(250, "2.1.0 OK")

    async def do_MAIL(self):
        """
        Send response to MAIL TO verb.

        .. note::

           Checks to see if ``SIZE=`` is passed, pass function off to have it's
           size handled.
        """
        if "size=" in self._line.lower():
            await self._size_in_mail()
        else:
            await self.push(250, "2.1.0 OK")

    async def help_RCPT(self):
        """
        Send response to the RCPT TO verb.

        https://kura.gg/blackhole/communicating-with-blackhole.html#help
        """
        await self.push(250, "Syntax: RCPT TO: <address>")

    async def do_RCPT(self):
        """Send response to RCPT TO verb."""
        await self.push(250, "2.1.5 OK")

    async def help_DATA(self):
        """
        Send help for the DATA verb.

        https://kura.gg/blackhole/communicating-with-blackhole.html#help
        """
        await self.push(250, "Syntax: DATA")

    def process_header(self, line):
        """
        Process dynamic switch email headers.

        Reads x-blackhole-delay and x-blackhole-mode headers and re-configures
        on-the-fly how the email is handled based on these headers.

        https://kura.gg/blackhole/dynamic-switches.html

        :param str line: An email header.
        """
        logger.debug(f"HEADER RECV: {line}")
        if self.config.dynamic_switch is False:
            logger.debug("Dynamic switches disabled, ignoring")
            return
        if self._disable_dynamic_switching is True:
            logger.debug("Dynamic switches are disabled by flags option.")
            return
        key, value = line.split(":")
        key, value = key.lower().strip(), value.lower().strip()
        if key == "x-blackhole-delay":
            self.delay = value
        if key == "x-blackhole-mode":
            self.mode = value

    async def response_from_mode(self):
        """
        Send a response based on the configured response mode.

        https://kura.gg/blackhole/dynamic-switches.html#dynamic-delay-switches
        https://kura.gg/blackhole/configuration.html#mode

        Response mode is configured in configuration file and can be overridden
        by email headers, if enabled.
        """
        logger.debug(f"MODE: {self.mode}")
        if self.mode == "bounce":
            key = random.choice(list(self._bounce_responses.keys()))  # nosec
            await self.push(key, self._bounce_responses[key])
        elif self.mode == "random":
            resps = {250: f"2.0.0 OK: queued as {self.message_id}"}
            resps.update(self._bounce_responses)
            key = random.choice(list(resps.keys()))  # nosec
            await self.push(key, resps[key])
        else:
            msg = f"2.0.0 OK: queued as {self.message_id}"
            await self.push(250, msg)

    async def do_DATA(self):
        r"""
        Send response to DATA verb and wait for mail data.

        This method will also implement timeout management and handling after
        receiving the DATA command and no new data is received.

        This method also implements the delay functionality, delaying a
        response after the final '\r\n.\r\n' line. --
        https://kura.gg/blackhole/configuration.html#delay
        https://kura.gg/blackhole/dynamic-switches.html#dynamic-delay-switches

        This method implements restrictions on message sizes. --
        https://kura.gg/blackhole/configuration.html#max-message-size
        """
        await self.push(354, "End data with <CR><LF>.<CR><LF>")
        on_body = False
        msg = []
        while not self.connection_closed:
            line = await self.wait()
            logger.debug(f"RECV {line}")
            msg.append(line)
            if line.lower().startswith(b"x-blackhole") and on_body is False:
                self.process_header(line.decode("utf-8").rstrip("\n"))
            if line == b"\n":
                on_body = True
            if line == b".\r\n":
                break
        if len(b"".join(msg)) > self.config.max_message_size:
            msg = []
            await self.push(
                552,
                "Message size exceeds fixed maximum message size",
            )
            return
        if self.delay:
            logger.debug(f"DELAYING RESPONSE: {self.delay} seconds")
            await asyncio.sleep(self.delay)
        await self.response_from_mode()

    async def do_STARTTLS(self):
        """STARTTLS is not implemented."""
        # It's currently not possible to implement STARTTLS due to lack of
        # support in asyncio. - https://bugs.python.org/review/23749/
        await self.do_NOT_IMPLEMENTED()

    async def help_NOOP(self):
        """
        Send help for the NOOP verb.

        https://kura.gg/blackhole/communicating-with-blackhole.html#help
        """
        await self.push(250, "Syntax: NOOP")

    async def do_NOOP(self):
        """Send response to the NOOP verb."""
        await self.push(250, "2.0.0 OK")

    async def help_RSET(self):
        """
        Send help for the RSET verb.

        https://kura.gg/blackhole/communicating-with-blackhole.html#help
        """
        await self.push(250, "Syntax: RSET")

    async def do_RSET(self):
        """
        Send response to the RSET verb.

        A new message id is generated and assigned.
        """
        old_msg_id = self.message_id
        self.message_id = message_id(self.fqdn)
        logger.debug(f"{old_msg_id} is now {self.message_id}")
        await self.push(250, "2.0.0 OK")

    async def help_VRFY(self):
        """
        Send help for the VRFY verb.

        https://kura.gg/blackhole/communicating-with-blackhole.html#help
        """
        await self.push(250, "Syntax: VRFY <address>")

    async def do_VRFY(self):
        """
        Send response to the VRFY verb.

            >>> VRFY pass=user@domain.tld
            250 2.0.0 <pass=user@domain.tld> OK

            >>> VRFY fail=user@domain.tld
            550 5.7.1 <fail=user@domain.tld> unknown

            >>> VRFY user@domain.tld
            252 2.0.0 Will attempt delivery

        .. note::

           If the request contains 'pass=', the server will respond with code
           250. If the request contains 'fail=', the server will respond with
           code 550. And finally, if neither flag is found, the server will
           respond with code 252.
        """
        _, addr = self._line.split(" ")
        if "pass=" in self._line:
            await self.push(250, f"2.0.0 <{addr}> OK")
        elif "fail=" in self._line:
            await self.push(550, f"5.7.1 <{addr}> unknown")
        else:
            await self.push(252, "2.0.0 Will attempt delivery")

    async def help_EXPN(self):
        """
        Send help for the EXPN verb.

        https://kura.gg/blackhole/communicating-with-blackhole.html#help
        """
        await self.push(250, "Syntax: EXPN <list1 | list2 | list3 | all>")

    async def _expn_value_to_list(self):
        """
        Look up and return a mailing list or generate one for EXPN all.

        :returns: A list of members for a mailing list.
        :rtype: :py:obj:`list`
        """
        _, expn = self._line.lower().split(" ")
        expn = expn.replace("<", "").replace(">", "")
        lists = {
            "list1": ("Shadow", "Wednesday", "Low-key Liesmith"),
            "list2": (
                "Jim Holden",
                "Naomi Nagata",
                "Alex Kamal",
                "Amos Burton",
            ),
            "list3": (
                "Takeshi Kovacs",
                "Laurens Bancroft",
                "Kristin Ortega",
                "Quellcrist Falconer",
                "Virginia Vidaura",
                "Reileen Kawahara",
            ),
        }
        if expn == "all":
            iterator = []
            for key in lists.keys():
                iterator.extend(lists[key])
            return iterator
        else:
            return lists[expn]

    async def _expn_response(self):
        """
        Generate response for an EXPN query.

        :returns: A list of responses.
        :rtype: :py:obj:`list`
        """
        iterator = await self._expn_value_to_list()
        i, resp = 1, []
        for item in iterator:
            start = "250-"
            if len(iterator) == i:
                start = "250 "
            user = item.lower().replace(" ", ".")
            resp.append(f"{start}{item} <{user}@{self.fqdn}>")
            i += 1
        return resp

    async def do_EXPN(self):
        """
        Handle the EXPN verb.

            >>> EXPN fail=test-list
            550 Not authorised

            >>> EXPN list1
            250-Shadow <shadow@blackhole.io>
            250-Wednesday <wednesday@blackhole.io>
            250 Low-key Liesmith <low-key.liesmith@blackhole.io>

            >>> EXPN list2
            250-Jim Holden <jim.holden@blackhole.io>
            250-Naomi Nagata <naomi.nagata@blackhole.io>
            250-Alex Kamal <alex.kamal@blackhole.io>
            250 Amos Burton <amos.burton@blackhole.io>

            >>> EXPN list3
            250-Takeshi Kovacs <takeshi.kovacs@blackhole.io>
            250-Laurens Bancroft <laurens.bancroft@blackhole.io>
            250-Kristin Ortega <kristin.ortega@blackhole.io>
            250-Quellcrist Falconer <quellcrist.falconer@blackhole.io>
            250-Virginia Vidaura <virginia.vidaura@blackhole.io>
            250 Reileen Kawahara <reileen.kawahara@blackhole.io>

            >>> EXPN all
            250-Shadow <shadow@blackhole.io>
            250-Wednesday <wednesday@blackhole.io>
            250-Low-key Liesmith <low-key.liesmith@blackhole.io>
            250-Takeshi Kovacs <takeshi.kovacs@blackhole.io>
            250-Laurens Bancroft <laurens.bancroft@blackhole.io>
            250-Kristin Ortega <kristin.ortega@blackhole.io>
            250-Quellcrist Falconer <quellcrist.falconer@blackhole.io>
            250-Virginia Vidaura <virginia.vidaura@blackhole.io>
            250-Reileen Kawahara <reileen.kawahara@blackhole.io>
            250-Jim Holden <jim.holden@blackhole.io>
            250-Naomi Nagata <naomi.nagata@blackhole.io>
            250-Alex Kamal <alex.kamal@blackhole.io>
            250 Amos Burton <amos.burton@blackhole.io>

            >>> EXPN list-does-not-exist
            550 Not authorised

        .. note::

           If EXPN contains 'fail=' or does not specify a mailing list the
           command will return a 550 code.
           Valid lists are: `list1`, `list2`, `list3` and `all`.
        """
        if "fail=" in self._line:
            await self.push(550, "Not authorised")
            return
        try:
            _, expn = self._line.lower().split(" ")
            expn = expn.replace("<", "").replace(">", "")
        except ValueError:
            await self.push(550, "Not authorised")
            return
        if expn not in ("list1", "list2", "list3", "all"):
            await self.push(550, "Not authorised")
            return
        for response in await self._expn_response():
            response = f"{response}\r\n".encode("utf-8")
            logger.debug(f"SENT {response}")
            self._writer.write(response)
        await self._writer.drain()

    async def help_ETRN(self):
        """
        Send help for the ETRN verb.

        https://kura.gg/blackhole/communicating-with-blackhole.html#help
        """
        await self.push(250, "Syntax: ETRN")

    async def do_ETRN(self):
        """Send response to the ETRN verb."""
        await self.push(250, "Queueing started")

    async def help_QUIT(self):
        """
        Send help for the QUIT verb.

        https://kura.gg/blackhole/communicating-with-blackhole.html#help
        """
        await self.push(250, "Syntax: QUIT")

    async def do_QUIT(self):
        """
        Send response to the QUIT verb.

        Closes the client connection.
        """
        await self.push(221, "2.0.0 Goodbye")
        self._handler_coroutine.cancel()
        await self.close()

    async def do_NOT_IMPLEMENTED(self):
        """Send a not implemented response."""
        await self.push(500, "Not implemented")

    async def help_UNKNOWN(self):
        """Send available help verbs when an invalid verb is received."""
        msg = " ".join(self.get_help_members())
        await self.push(501, f"Supported commands: {msg}")

    async def do_UNKNOWN(self):
        """Send response to unknown verb."""
        self._failed_commands += 1
        if self._failed_commands > 9:
            await self.push(502, "5.5.3 Too many unknown commands")
            await self.close()
        else:
            await self.push(502, "5.5.2 Command not recognised")

    @property
    def delay(self):
        """
        Delay after the DATA command completes.

        Value is in seconds, with a maximum value of 60 seconds.

        https://kura.gg/blackhole/configuration.html#delay
        https://kura.gg/blackhole/dynamic-switches.html#dynamic-delay-switches

        :returns: A delay time in seconds. Default: ``None``.
        :rtype: :py:obj:`int` or :py:obj:`None`
        """
        if "delay" in self._flags.keys():
            delay = self._flags["delay"]
            if isinstance(delay, list):
                self._delay_range(delay)
                return self._delay
            return int(delay)
        if self._delay is not None:
            return self._delay
        if self.config.delay is not None:
            return self.config.delay
        return None

    @delay.setter
    def delay(self, values):
        logger.debug("DELAY: Dymanic delay enabled")
        value = values.split(",")
        if len(value) == 2:
            self._delay_range(value)
        elif len(value) == 1:
            self._delay_single(value[0])
        else:
            logger.debug(f"DELAY: Invalid value(s): {values}. Skipping")
            return

    def _delay_range(self, value):
        """
        Generate a delay from a range provided in the email header.

        https://kura.gg/blackhole/configuration.html#delay
        https://kura.gg/blackhole/dynamic-switches.html#dynamic-delay-switches

        :param str value: A list of minimum and maximum values as a string.
                          i.e. (10, 20).

        .. note::

           Converted from a string of a list to a list of integers.
        """
        min_delay, max_delay = value
        min_delay, max_delay = min_delay.strip(), max_delay.strip()
        try:
            min_delay = int(min_delay)
            max_delay = int(max_delay)
        except ValueError:
            logger.debug(
                f"DELAY: Unable to convert {min_delay}, {max_delay} to "
                "integers. Skipping",
            )
            self._delay = None
            return
        if min_delay < 0 or max_delay < 0:
            logger.debug(
                f"DELAY: A value is less than 0: {min_delay}, {max_delay}. "
                "Skipping",
            )
            self._delay = None
            return
        if min_delay > max_delay:
            logger.debug("Min cannot be greater than max")
            self._delay = None
            return
        if max_delay > self._max_delay:
            logger.debug(
                f"DELAY: {max_delay} is higher than {self._max_delay}. "
                f"{self._max_delay} is the hard coded maximum delay for "
                "security.",
            )
            max_delay = self._max_delay
        self._delay = random.randint(min_delay, max_delay)  # nosec
        logger.debug(
            f"DELAY: Set to {self._delay} from range {min_delay}-{max_delay}",
        )
        return

    def _delay_single(self, value):
        """
        Generate a delay from a value provided in an email header.

        https://kura.gg/blackhole/configuration.html#delay
        https://kura.gg/blackhole/dynamic-switches.html#dynamic-delay-switches

        :param str value: Time in seconds as a string.

        .. note:

           Converted from a string to an integer.
        """
        try:
            value = int(value)
        except ValueError:
            logger.debug(
                f"DELAY: Unable to convert {value} to an integer. Skipping",
            )
            self._delay = None
            return
        logger.debug(value)
        if value < 0:
            logger.debug(f"DELAY: {value} is less than 0. Skipping")
            self._delay = None
            return
        if value > self._max_delay:
            logger.debug(
                f"DELAY: {value} is higher than {self._max_delay}. "
                f"{self._max_delay} is the hard coded maximum delay for "
                "security.",
            )
            self._delay = self._max_delay
            return
        logger.debug(f"DELAY: Set to {value}")
        self._delay = value

    @property
    def mode(self):
        """
        How to respond to an email, based on configuration.

        Response is configured in the configuration file or configured from
        email headers, if configured to allow that option.

        https://kura.gg/blackhole/configuration.html#mode
        https://kura.gg/blackhole/dynamic-switches.html#dynamic-mode-switches

        :returns: A response mode.
        :rtype: :py:obj:`str`
        """
        if "mode" in self._flags.keys():
            return self._flags["mode"]
        if self._mode is not None:
            return self._mode
        return self.config.mode

    @mode.setter
    def mode(self, value):
        if value not in ("accept", "bounce", "random"):
            logger.debug(
                f"MODE: {value} is an invalid. Allowed modes: (accept, "
                "bounce, random)",
            )
            self._mode = None
            return
        logger.debug(f"MODE: Dynamic mode enabled. Mode set to {value}")
        self._mode = value
