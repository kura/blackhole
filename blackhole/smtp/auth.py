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

import base64
import inspect
import logging


__all__ = ('Auth', )


logger = logging.getLogger('blackhole.smtp.auth')


class Auth:

    def get_auth_members(self):
        """
        Get a list of available AUTH mechanisms.

        :returns: A list of available authentication mechanisms.
        :rtype: :any:`list`
        """
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        cmds = []
        for cmd, _ in members:
            if cmd.startswith('auth_') and cmd != 'auth_UNKNOWN':
                cmd = cmd.replace('auth_', '').replace('_', '-')
                cmds.append(cmd)
        return cmds

    def lookup_auth_handler(self, line):
        """
        Look up a handler for the received AUTH mechanism.

        :param line: A line of data from a client.
        :type line: :any:`str`
        :returns: A callable authentication mechanism.
        :rtype: :any:`blackhole.smtp.Smtp.auth_MECHANISM`

        .. note::

        Using ``pass=`` as part of the auth data will trigger an
        authentication pass, using ``fail=`` will trigger an authentication
        failure.
        """
        parts = line.split(' ')
        if len(parts) < 2:
            return self.auth_UNKNOWN
        mechanism = parts[1].upper()
        if mechanism == 'CRAM-MD5':
            return self.auth_CRAM_MD5
        if mechanism not in self.get_auth_members():
            return self.auth_UNKNOWN
        if len(parts) == 3 and mechanism == 'PLAIN':
            if 'fail=' in line:
                return self._auth_failure
            return self._auth_success
        return getattr(self, 'auth_{}'.format(mechanism.upper()),
                       self.auth_UNKNOWN)

    async def auth_UNKNOWN(self):
        """Response to an unknown auth mechamism."""
        await self.push(501, '5.5.4 Syntax: AUTH mechanism')

    async def help_AUTH(self):
        """
        Send help for AUTH mechanisms.

        https://blackhole.io/index.html#help-verb
        """
        mechanisms = ' '.join(self.get_auth_members())
        await self.push(250, 'Syntax: AUTH {}'.format(mechanisms))

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
        await self.push(334, 'VXNlcm5hbWU6')
        line = await self.wait()
        logger.debug('RECV %s', line)
        if b'fail=' in line.lower():
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
        message_id = base64.b64encode(self.message_id.encode('utf-8'), b'==')
        await self.push(334, message_id.decode('utf-8'))
        line = await self.wait()
        logger.debug('RECV %s', line)
        if b'fail=' in line.lower():
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
        await self.push(334, ' ')
        line = await self.wait()
        logger.debug('RECV %s', line)
        if b'fail=' in line.lower():
            await self._auth_failure()
        else:
            await self._auth_success()

    async def _auth_success(self):
        """Send an authentication successful response."""
        await self.push(235, '2.7.0 Authentication successful')

    async def _auth_failure(self):
        """Send an authentication failure response."""
        await self.push(535, '5.7.8 Authentication failed')
