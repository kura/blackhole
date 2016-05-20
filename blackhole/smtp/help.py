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

import inspect
import logging


__all__ = ('Help', )


logger = logging.getLogger('blackhole.smtp.auth')


class Help:

    def lookup_help_handler(self, parts):
        """
        Look up a help handler for the SMTP VERB.

        https://blackhole.io/index.html#help-verb

        :param parts: A list of command data, split on spaces.
        :type parts: :any:`list`
        :returns: A callable help handler.
        :rtype: :any:`blackhole.smtp.Smtp.help_VERB`
        """
        if len(parts) > 1:
            cmd = 'help_{}'.format(parts[1].upper())
        else:
            cmd = 'do_HELP'
        return getattr(self, cmd, self.help_UNKNOWN)

    def get_help_members(self):
        """
        Get a list of HELP handlers for verbs.

        https://blackhole.io/index.html#help-verb

        :returns: A list of available help handlers.
        :rtype: :any:`list`
        """
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        cmds = []
        for cmd, _ in members:
            if cmd.startswith('help_') and not cmd == 'help_UNKNOWN':
                cmds.append(cmd.replace('help_', ''))
        return cmds

    async def do_HELP(self):
        """
        Send a response to the HELP verb.

        https://blackhole.io/index.html#help-verb
        """
        msg = ' '.join(self.get_help_members())
        await self.push(250, 'Supported commands: {}'.format(msg))

    async def help_HELO(self):
        """
        Send help for HELO verb.

        https://blackhole.io/index.html#help-verb
        """
        await self.push(250, 'Syntax: HELO domain.tld')

    async def help_EHLO(self):
        """
        Send help for the EHLO verb.

        https://blackhole.io/index.html#help-verb
        """
        await self.push(250, 'Syntax: EHLO domain.tld')

    async def help_MAIL(self):
        """
        Send help for the MAIL TO verb.

        https://blackhole.io/index.html#help-verb
        """
        await self.push(250, 'Syntax: MAIL FROM: <address>')

    async def help_RCPT(self):
        """
        Send response to the RCPT TO verb.

        https://blackhole.io/index.html#help-verb
        """
        await self.push(250, 'Syntax: RCPT TO: <address>')

    async def help_DATA(self):
        """
        Send help for the DATA verb.

        https://blackhole.io/index.html#help-verb
        """
        await self.push(250, 'Syntax: DATA')

    async def help_STARTTLS(self):
        """Send help for the STARTTLS command."""
        await self.push(250, 'Syntax: STARTTLS')

    async def help_NOOP(self):
        """
        Send help for the NOOP verb.

        https://blackhole.io/index.html#help-verb
        """
        await self.push(250, 'Syntax: NOOP')

    async def help_RSET(self):
        """
        Send help for the RSET verb.

        https://blackhole.io/index.html#help-verb
        """
        await self.push(250, 'Syntax: RSET')

    async def help_VRFY(self):
        """
        Send help for the VRFY verb.

        https://blackhole.io/index.html#help-verb
        """
        await self.push(250, 'Syntax: VRFY <address>')

    async def help_EXPN(self):
        """
        Send help for the EXPN verb.

        https://blackhole.io/index.html#help-verb
        """
        await self.push(250, 'Syntax: EXPN <list1 | list2 | list3 | all>')

    async def help_ETRN(self):
        """
        Send help for the ETRN verb.

        https://blackhole.io/index.html#help-verb
        """
        await self.push(250, 'Syntax: ETRN')

    async def help_QUIT(self):
        """
        Send help for the QUIT verb.

        https://blackhole.io/index.html#help-verb
        """
        await self.push(250, 'Syntax: QUIT')

    async def help_UNKNOWN(self):
        """Send available help verbs when an invalid verb is received."""
        msg = ' '.join(self.get_help_members())
        await self.push(501, 'Supported commands: {}'.format(msg))
