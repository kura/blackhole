# -*- coding: utf-8 -*-

# (The MIT License)
#
# Copyright (c) 2013-2018 Kura
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

"""Provides the Imap protocol wrapper."""


import asyncio
import logging
from typing import Any, Callable, List, Optional

from blackhole.config import Config
from .protocols import StreamReaderProtocol


__all__ = ('Imap', )
"""Tuple all the things."""


logger = logging.getLogger('blackhole.imap')


class Imap(StreamReaderProtocol):
    CAPABILITY = ('CAPABILITY', 'IMAP4rev1', 'LITERAL+', 'SASL-IR',
                  'LOGIN-REFERRALS', 'ID', 'ENABLE', 'IDLE', 'AUTH=PLAIN',
                  'AUTH=LOGIN', )
    LOGIN_CAPABILITY = ('CAPABILITY', 'IMAP4rev1', 'LITERAL+', 'SASL-IR',
                        'LOGIN-REFERRALS', 'ID', 'ENABLE', 'IDLE', 'SORT',
                        'SORT=DISPLAY', 'THREAD=REFERENCES', 'THREAD=REFS',
                        'THREAD=ORDEREDSUBJECT', 'MULTIAPPEND', 'URL-PARTIAL',
                        'CATENATE', 'UNSELECT', 'CHILDREN', 'NAMESPACE',
                        'UIDPLUS', 'LIST-EXTENDED', 'I18NLEVEL=1', 'CONDSTORE',
                        'QRESYNC', 'ESEARCH', 'ESORT', 'SEARCHRES', 'WITHIN',
                        'CONTEXT=SEARCH', 'LIST-STATUS', 'BINARY', 'MOVE',
                        'SPECIAL-USE', )

    _var = None
    _verb = None
    _ext = None
    _logged_in = False
    _failed_commands = 0

    def __init__(self, clients: List,
                 loop: Optional[asyncio.BaseEventLoop] = None) -> None:
        super().__init__(clients, loop)

    def connection_made(self, transport: asyncio.transports.Transport) -> None:
        """
        Tie a connection to blackhole to the IMAP protocol.

        :param asyncio.transports.Transport transport: The transport class.
        """
        super().connection_made(transport)
        logger.debug('Peer connected')
        self.transport = transport
        self.flags_from_transport()
        self.connection_closed = False
        self._handler_coroutine = self.loop.create_task(self._handle_client())

    def reset(self) -> None:
        self._verb, self._var = None, None

    async def _handle_client(self) -> None:
        await self.greet()
        while not self.connection_closed:
            self.reset()
            line = await self.wait()
            logger.debug('RECV %s', line)
            line = line.decode('utf-8').rstrip('\r\n')
            self.deconstruct(line)
            handler = self.lookup_handler()
            logger.debug(handler)
            if handler:
                await handler()
            else:
                await self.do_UNKNOWN()

    def deconstruct(self, line: str) -> None:
        parts = line.split(' ', 2)
        if len(parts) == 2:
            self._var, self._verb = parts
        elif len(parts) > 2:
            self._var, self._verb = parts[0], parts[1], self._ext = parts[2:]

    def lookup_handler(self) -> Callable:
        logger.debug('looking up do_%s', self._verb)
        if self._var is None or self._verb is None:
            return self.do_UNKNOWN
        return getattr(self, 'do_{0}'.format(self._verb.upper()),
                       self.do_UNKNOWN)

    async def greet(self) -> None:
        capability = ' '.join(self.CAPABILITY)
        await self.push('* OK [{0}] Blackhole ready'.format(capability))

    async def do_CAPABILITY(self) -> None:
        if self._logged_in is False:
            capability = ' '.join(self.CAPABILITY)
            msg = ('{0} OK Pre-login capabilities listed, post-login '
                   'capabilities have more').format(self._var)
        else:
            capability = ' '.join(self.LOGIN_CAPABILITY)
            msg = '{0} OK Capability completed'.format(self._var)
        await self.push('* {0}'.format(capability))
        await self.push(msg)

    async def do_CLOSE(self) -> None:
        await self.push('{0} OK Close completed'.format(self._var))

    async def do_ENABLE(self) -> None:
        await self.push('{0} OK Enabled'.format(self._var))

    async def do_ID(self) -> None:
        await self.push('{0} ("name" "Blackhole")'.format(self._var))

    async def do_IDLE(self) -> None:
        await self.push('+ idling')

    async def do_LIST(self) -> None:
        await self.push(r'* LIST (\HasNoChildren) "." "INBOX"')
        await self.push('{0} OK List completed'.format(self._var))

    async def do_LOGIN(self) -> None:
        msg = ' '.join(self.LOGIN_CAPABILITY)
        self._logged_in = True
        await self.push('{0} OK {1} Logged in'.format(self._var, msg))

    async def do_LOGOUT(self) -> None:
        self._logged_in = False
        await self.push('* BYE Logging out')
        await self.push('{0} OK Logout complete'.format(self._var))
        self._handler_coroutine.cancel()
        await self.close()

    async def do_QUIT(self) -> None:
        await self.push('DONE')
        self._handler_coroutine.cancel()
        await self.close()

    async def do_SEARCH(self) -> None:
        await self.push('* SEARCH')
        await self.push('{0} OK Search completed'.format(self._var))

    async def do_SELECT(self) -> None:
        # mailbox = self._line.split(' ')[2]
        await self.push(r'* FLAGS (\Draft \Answered \Flagged \Deleted \Seen '
                        '\Recent)')
        await self.push(r'* OK [PERMANENTFLAGS (\Draft \Answered \Flagged '
                        '\Deleted \Seen \*)] Limited')
        await self.push('* 10 EXISTS')
        await self.push('* 1 RECENT')
        await self.push('* OK [UIDVALIDITY 1021381622] OK')
        await self.push('* OK [UIDNEXT 11] Predicted next UID')
        await self.push('{0} OK [READ-WRITE OK]'.format(self._var))

    async def timeout(self) -> None:
        await self.push('* BYE Timeout')
        await self.close()

    async def do_UNKNOWN(self) -> None:
        self._failed_commands += 1
        msg = 'BAD Error in IMAP command'
        if self._failed_commands == 3:
            await self.push('* BYE Too many invalid IMAP commands.')
            await self.close()
            return
        if self._verb:
            await self.push('{0} {1}'.format(msg, self._verb))
        else:
            await self.push(msg)
