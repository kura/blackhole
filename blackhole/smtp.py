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

"""
blackhole.smtp.

This module contains the Smtp protocol.
"""


import asyncio
import logging
import random

from blackhole.config import Config
from blackhole.utils import mailname, message_id


logger = logging.getLogger('blackhole.smtp')


class Smtp(asyncio.StreamReaderProtocol):
    """The class responsible for handling SMTP/SMTPS commands."""

    bounce_responses = {
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
    """A dictionary of response codes and messages for bouncing mail."""

    def __init__(self):
        """
        Initialise the SMTP parotocol.

        .. note::

           Loads the configuration, defines the server's FQDN and generates
           a RFC 2822 Message-ID.
        """
        self.loop = asyncio.get_event_loop()
        super().__init__(
            asyncio.StreamReader(loop=self.loop),
            client_connected_cb=self._client_connected_cb,
            loop=self.loop)
        self.config = Config()
        self.fqdn = mailname()
        self.message_id = message_id()

    def connection_made(self, transport):
        """
        Tie a connection to blackhole to the SMTP protocol.

        :param transport:
        :type transport: `asyncio.transport.Transport`
        """
        super().connection_made(transport)
        self.peer = transport.get_extra_info('peername')
        logger.debug('Peer %s connected', repr(self.peer))
        self.transport = transport
        self.connection_closed = False
        self._handler_coroutine = self.loop.create_task(self._handle_client())

    def _client_connected_cb(self, reader, writer):
        """
        Callback that binds a stream reader and writer to the SMTP Protocol.

        :param reader:
        :type reader: `asyncio.streams.StreamReader`
        :param writer:
        :type writer: `asyncio.streams.StreamWriter`
        """
        self._reader = reader
        self._writer = writer

    def connection_lost(self, exc):
        """Callback for when a connection is closed or lost."""
        logger.debug('Peer %s disconnected', repr(self.peer))
        super().connection_lost(exc)
        self._connection_closed = True

    async def _handle_client(self):
        """
        Handle a connection to the server.

        This method greets the client and then accepts and handles each line
        the client sends, passing off to the currect verb handler.

        Client timeout is also managed and handled here.
        """
        await self.greet()
        while not self.connection_closed:
            try:
                line = await asyncio.wait_for(self._reader.readline(),
                                              self.config.timeout,
                                              loop=self.loop)
            except asyncio.TimeoutError:
                await self.timeout()
            logger.debug('RECV %s', line)
            line = line.decode('utf-8').rstrip('\r\n')
            parts = line.split(None, 1)
            if parts:
                verb = parts[0]
                logger.debug("RECV VERB %s", verb)
                handler = self.lookup_handler(verb) or self.do_UNKNOWN
                logger.debug("USING %s", handler.__name__)
                await handler()

    async def timeout(self):
        """
        Timeout a client connection.

        Sends the 421 timeout message to the client and closes the connection.
        """
        logger.debug('%s timed out, no data received for %d seconds',
                     repr(self.peer), self.config.timeout)
        await self.push(421, 'Timeout')
        await self.close()

    async def close(self):
        """Close the connection from the client."""
        logger.debug('Closing connection: %s', repr(self.peer))
        if self._writer:
            self._writer.close()
        self._connection_closed = True

    def lookup_handler(self, verb):
        """
        Look up the SMTP VERB against a handler.

        :param verb:
        :type verb: str -- i.e. HELO, EHLO, DATA etc.
        :returns: `blackhole.smtp.do_VERB`.
        """
        cmd = "do_{}".format(verb.upper())
        return getattr(self, cmd, None)

    async def push(self, code, msg):
        """
        Write a response code and message to the client.

        :param code:
        :type int: SMTP code, i.e. 250.
        :param msg:
        :type msg: The message for the SMTP code.
        """
        response = "{} {}\r\n".format(code, msg).encode('utf-8')
        logger.debug('SEND %s', response)
        self._writer.write(response)
        await self._writer.drain()

    async def greet(self):
        """Send a greeting to the client."""
        await self.push(220, '{} ESMTP'.format(self.fqdn))

    async def do_HELO(self):
        """Send response to HELO verb."""
        await self.push(250, 'OK')

    async def do_EHLO(self):
        """Send response to EHLO verb."""
        response = "250-{}\r\n".format(self.fqdn).encode('utf-8')
        self._writer.write(response)
        logger.debug('SENT %s', response)
        responses = ('250-PIPELINING', '250-SIZE 512000', '250-VRFY',
                     '250-ETRN', '250-ENHANCEDSTATUSCODES', '250-8BITMIME',
                     '250 DSN', )
        for response in responses:
            response = "{}\r\n".format(response).encode('utf-8')
            logger.debug("SENT %s", response)
            self._writer.write(response)
        await self._writer.drain()

    async def do_MAIL(self):
        """Send response to MAIL TO verb."""
        await self.push(250, '2.1.0 OK')

    async def do_RCPT(self):
        """Send response to RCPT TO verb."""
        await self.push(250, '2.1.5 OK')

    async def do_DATA(self):
        r"""
        Send response to DATA verb and wait for mail data.

        This method will also implement timeout management and handling after
        receiving the DATA command and no new data is received.

        This method also implements they delay functionality, delaying a
        response after the final '\r\n.\r\n' line.

        This method is also responsible handling the mode with which to
        respond to the client.
        """
        await self.push(354, 'End data with <CR><LF>.<CR><LF>')
        while not self.connection_closed:
            try:
                line = await asyncio.wait_for(self._reader.readline(),
                                              self.config.timeout,
                                              loop=self.loop)
            except asyncio.TimeoutError:
                await self.timeout()
            logger.debug('RECV %s', line)
            if line == b'.\r\n':
                break
        if self.config.delay:
            asyncio.sleep(self.config.delay)
        if self.config.mode == 'bounce':
            key = random.choice(list(self.bounce_responses.keys()))
            await self.push(key, self.bounce_responses[key])
        elif self.config.mode == 'random':
            resps = {250, '2.0.0 OK: queued as {}'.format(self.message_id), }
            resps.update(self.bounce_responses)
            key = random.choice(list(resps.keys()))
            await self.push(key, resps[key])
        else:
            msg = '2.0.0 OK: queued as {}'.format(self.message_id)
            await self.push(250, msg)

    async def do_STARTTLS(self):
        """STARTTLS is not implemented."""
        # It's currently not possible to implement STARTTLS due to lack of
        # support in asyncio. - https://bugs.python.org/review/23749/
        await self.do_UNKNOWN()

    async def do_NOOP(self):
        """Send response to the NOOP verb."""
        await self.push(250, '2.0.0 OK')

    async def do_RSET(self):
        """
        Send response to the RSET verb.

        A new message id is generated and assigned.
        """
        old_msg_id = self.message_id
        self.message_id = message_id()
        logger.debug('%s is now %s', old_msg_id, self.message_id)
        await self.push(250, '2.0.0 OK')

    async def do_VRFY(self):
        """Send response to the VRFY verb."""
        await self.push(252, '2.0.0 OK')

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

    async def do_UNKNOWN(self):
        """Send response to unknown verb."""
        await self.push(500, 'Not implemented')
