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

import logging


__all__ = ('Expn', )


logger = logging.getLogger('blackhole.smtp.expn')


class Expn:

    async def _expn_value_to_list(self):
        """
        Look up and return a mailing list or generate one for EXPN all.

        :returns: A list of members for a mailing list.
        :rtype: :any:``list``
        """
        _, expn = self._line.lower().split(' ')
        expn = expn.replace('<', '').replace('>', '')
        lists = {
            'list1': ('Shadow', 'Wednesday', 'Low-key Liesmith'),
            'list2': ('Jim Holden', 'Naomi Nagata', 'Alex Kamal',
                      'Amos Burton'),
            'list3': ('Takeshi Kovacs', 'Laurens Bancroft', 'Kristin Ortega',
                      'Quellcrist Falconer', 'Virginia Vidaura',
                      'Reileen Kawahara')
        }
        if expn == 'all':
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
        :rtype: :any:``list``
        """
        iterator = await self._expn_value_to_list()
        i, resp = 1, []
        for item in iterator:
            start = '250-'
            if len(iterator) == i:
                start = '250 '
            user = item.lower().replace(' ', '.')
            resp.append('{}{} <{}@{}>'.format(start, item, user, self.fqdn))
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
        if 'fail=' in self._line:
            await self.push(550, 'Not authorised')
            return
        try:
            _, expn = self._line.lower().split(' ')
            expn = expn.replace('<', '').replace('>', '')
        except ValueError:
            await self.push(550, 'Not authorised')
            return
        if expn not in ('list1', 'list2', 'list3', 'all'):
            await self.push(550, 'Not authorised')
            return
        for response in await self._expn_response():
            response = "{}\r\n".format(response).encode('utf-8')
            logger.debug("SENT %s", response)
            self._writer.write(response)
        await self._writer.drain()
