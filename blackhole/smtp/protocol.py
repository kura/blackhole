# (The MIT License)
#
# Copyright (c) 2016 Kura
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
import logging

from .auth import Auth
from .expn import Expn
from .help import Help
from .switch import Switch
from ..protocols import Protocol
from ..utils import message_id, get_version


__all__ = ('Smtp', )


logger = logging.getLogger('blackhole.smtp')


class Smtp(Protocol, Auth, Help, Switch, Expn):
    """The class responsible for handling SMTP/SMTPS commands."""

    _bounce_responses = {
        450: 'Requested mail action not taken: mailbox unavailable',
        451: 'Requested action aborted: local error in processing',
        452: 'Requested action not taken: insufficient system storage',
        458: 'Unable to queue message',
        521: 'Machine does not accept mail',
        550: 'Requested action not taken: mailbox unavailable',
        551: 'User not local',
        552: 'Requested mail action aborted: exceeded storage allocation',
        553: 'Requested action not taken: mailbox name not allowed',
        571: 'Blocked',
    }
    """The response code and message for each bounce type."""

    _delay = None
    """The delay timer value."""

    _max_delay = 60
    """The maximum delay value in seconds. Cannot be more than 60 seconds."""

    _mode = None
    """The response mode to use."""

    _disable_dynamic_switching = False
    """
    This option disabled dynamic switching functionality.

    Dynamic switching will be disabled when mode= and delay= flags are
    configured.

    https://blackhole.io/configuration-options.html#listen
    https://blackhole.io/configuration-options.html#tls_listen
    """

    _failed_commands = 0
    """An internal counter of failed commands for a client."""

    def __init__(self, clients, flags, loop=None):
        """
        Initialise the SMTP protocol.

        :param clients: A list of connected clients.
        :type clients: :any:`list`
        :param loop: The event loop to use.
        :type loop: :any:`None` or
                    :any:`syncio.unix_events._UnixSelectorEventLoop`

        .. note::

           Loads the configuration, defines the server's FQDN and generates
           an RFC 2822 Message-ID.
        """
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        super().__init__(clients, flags, loop=loop)
        self.message_id = message_id(self.fqdn)
        self.banner = '{} ESMTP/{}'.format(self.fqdn, get_version())

    async def _handle_client(self):
        """
        Handle a client connection.

        This method greets the client and then accepts and handles each line
        the client sends, passing off to the currect verb handler.
        """
        await self.greet()
        while not self.connection_closed:
            line = await self.wait()
            if line is None:
                await self.close()
                return
            logger.debug('RECV %s', line)
            line = line.decode('utf-8').rstrip('\r\n')
            self._line = line
            handler = self.lookup_handler(line)
            if handler:
                await handler()
            else:
                await self.push(502, '5.5.2 Command not recognised')

    async def wait(self):
        """
        Wait for data from the client.

        :returns: A line of received data.
        :rtype: :any:`str`

        .. note::

           Also handles client timeouts if they wait too long before sending
           data. -- https://blackhole.io/configuration-options.html#timeout
        """
        while not self.connection_closed:
            try:
                line = await asyncio.wait_for(self._reader.readline(),
                                              self.config.timeout,
                                              loop=self.loop)
            except asyncio.TimeoutError:
                await self.timeout()
                return None
            return line

    async def timeout(self):
        """
        Timeout a client connection.

        Sends the 421 timeout message to the client and closes the connection.

        https://blackhole.io/configuration-options.html#timeout
        """
        logger.debug('Peer timed out, no data received for %d seconds',
                     self.config.timeout)
        await self.push(421, 'Timeout')
        await self.close()

    def lookup_handler(self, line):
        """
        Look up the SMTP VERB against a handler.

        :param line: Look up the command handler to use from the data provided.
        :type line: :any:`str`
        :returns: A callable command handler.
        :rtype: :any:`blackhole.smtp..Smtp.do_VERB`,
                  :any:`blackhole.smtp.Smtp.auth_MECHANISM`,
                  :any:`blackhole.smtp..Smtp.help_VERB`
        """
        parts = line.split(None, 1)
        if parts:
            if parts[0].lower() == 'help':
                return self.lookup_help_handler(parts)
            if parts[0].lower() == 'auth':
                return self.lookup_auth_handler(line)
            else:
                return self.lookup_verb_handler(parts[0])
        return self.do_UNKNOWN

    def lookup_verb_handler(self, verb):
        """
        Look up a handler for the SMTP VERB.

        :param verb:
        :type verb: :any:`str`
        :returns: A callable command handler.
        :rtype: :any:`blackhole.smtp.Smtp.do_VERB`
        """
        return getattr(self, 'do_{}'.format(verb.upper()), self.do_UNKNOWN)

    async def push(self, code, msg):
        """
        Write a response code and message to the client.

        :param code: SMTP code, i.e. 250.
        :type code: :any:`int`
        :param msg: The message for the SMTP code
        :type msg: :any:`str`
        """
        response = "{} {}\r\n".format(code, msg).encode('utf-8')
        logger.debug('SEND %s', response)
        self._writer.write(response)
        await self._writer.drain()

    async def greet(self):
        """Send a greeting to the client."""
        await self.push(220, '{}'.format(self.banner))

    async def do_HELO(self):
        """Send response to HELO verb."""
        await self.push(250, 'OK')

    async def do_EHLO(self):
        """Send response to EHLO verb."""
        response = "250-{}\r\n".format(self.fqdn).encode('utf-8')
        self._writer.write(response)
        logger.debug('SENT %s', response)
        auth = ' '.join(self.get_auth_members())
        responses = ('250-HELP', '250-PIPELINING', '250-AUTH {}'.format(auth),
                     '250-SIZE {}'.format(self.config.max_message_size),
                     '250-VRFY', '250-ETRN', '250-ENHANCEDSTATUSCODES',
                     '250-8BITMIME', '250-SMTPUTF8', '250-EXPN', '250 DSN', )
        for response in responses:
            response = "{}\r\n".format(response).encode('utf-8')
            logger.debug("SENT %s", response)
            self._writer.write(response)
        await self._writer.drain()

    async def _size_in_mail(self):
        """
        Handle ``SIZE=`` being passed in ``MAIL`` verb.

        Send a 552 response if the size provided is larger than
        max_message_size.
        """
        parts = self._line.lower().split(' ')
        size = None
        for part in parts:
            if part.startswith('size='):
                size = part.split('=')[1]
        if (size is not None and size.isdigit() and
                int(size) > self.config.max_message_size):
            await self.push(552, 'Message size exceeds fixed maximum '
                                 'message size')
        else:
            await self.push(250, '2.1.0 OK')

    async def do_MAIL(self):
        """
        Send response to MAIL TO verb.

        .. note::

           Checks to see if ``SIZE=`` is passed, pass function off to have it's
           size handled.
        """
        if 'size=' in self._line.lower():
            await self._size_in_mail()
        else:
            await self.push(250, '2.1.0 OK')

    async def do_RCPT(self):
        """Send response to RCPT TO verb."""
        await self.push(250, '2.1.5 OK')

    async def do_DATA(self):
        r"""
        Send response to DATA verb and wait for mail data.

        This method will also implement timeout management and handling after
        receiving the DATA command and no new data is received.

        This method also implements the delay functionality, delaying a
        response after the final '\r\n.\r\n' line. --
        https://blackhole.io/configuration-options.html#delay
        https://blackhole.io/dynamic-switches.html#dynamic-delay-switches

        This method implements restrictions on message sizes. --
        https://blackhole.io/configuration-options.html#max-message-size
        """
        await self.push(354, 'End data with <CR><LF>.<CR><LF>')
        on_body = False
        msg = []
        while not self.connection_closed:
            line = await self.wait()
            logger.debug('RECV %s', line)
            msg.append(line)
            if line.lower().startswith(b'x-blackhole') and on_body is False:
                self.process_header(line.decode('utf-8').rstrip('\n'))
            if len(b''.join(msg)) > self.config.max_message_size:
                await self.push(552, 'Message size exceeds fixed maximum '
                                     'message size')
                return
            if line == b'\n':
                on_body = True
            if line == b'.\r\n':
                break
        if self.delay:
            logger.debug('DELAYING RESPONSE: %s seconds', self.delay)
            await asyncio.sleep(self.delay)
        await self.response_from_mode()

    async def do_STARTTLS(self):
        """STARTTLS is not implemented."""
        # It's currently not possible to implement STARTTLS due to lack of
        # support in asyncio. - https://bugs.python.org/review/23749/
        await self.do_NOT_IMPLEMENTED()

    async def do_NOOP(self):
        """Send response to the NOOP verb."""
        await self.push(250, '2.0.0 OK')

    async def do_RSET(self):
        """
        Send response to the RSET verb.

        A new message id is generated and assigned.
        """
        old_msg_id = self.message_id
        self.message_id = message_id(self.fqdn)
        logger.debug('%s is now %s', old_msg_id, self.message_id)
        await self.push(250, '2.0.0 OK')

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
        _, addr = self._line.split(' ')
        if 'pass=' in self._line:
            await self.push(250, '2.0.0 <{}> OK'.format(addr))
        elif 'fail=' in self._line:
            await self.push(550, '5.7.1 <{}> unknown'.format(addr))
        else:
            await self.push(252, '2.0.0 Will attempt delivery')

    async def do_ETRN(self):
        """Send response to the ETRN verb."""
        await self.push(250, 'Queueing started')

    async def do_QUIT(self):
        """
        Send response to the QUIT verb.

        Closes the client connection.
        """
        await self.push(221, '2.0.0 Goodbye')
        self._handler_coroutine.cancel()
        await self.close()

    async def do_NOT_IMPLEMENTED(self):
        """Send a not implemented response."""
        await self.push(500, 'Not implemented')

    async def do_UNKNOWN(self):
        """Send response to unknown verb."""
        self._failed_commands += 1
        if self._failed_commands > 9:
            await self.push(502, '5.5.3 Too many unknown commands')
            await self.close()
        else:
            await self.push(502, '5.5.2 Command not recognised')
