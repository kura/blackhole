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

import collections


__all__ = ('error', )


_status = {'400': {'ascii': ('    44    00000   00000\n'
                             '   444   00   00 00   00\n'
                             ' 44  4   00   00 00   00\n'
                             '44444444 00   00 00   00\n'
                             '   444    00000   00000\n'),
                   'binary': '001101000011000000110000',
                   'reason': 'Bad Request'},
           '404': {'ascii': ('    44    00000      44\n'
                             '   444   00   00    444\n'
                             ' 44  4   00   00  44  4\n'
                             '44444444 00   00 44444444\n'
                             '   444    00000     444\n'),
                   'binary': '001101000011000000110100',
                   'reason': 'Not Found'},
           '403': {'ascii': ('    44    00000  333333\n'
                             '   444   00   00    3333\n'
                             ' 44  4   00   00   3333\n'
                             '44444444 00   00     333\n'
                             '   444    00000  333333\n'),
                   'binary': '00110100 00110000 00110011',
                   'reason': 'Forbidden'},
           '405': {'ascii': ('    44    00000  555555\n'
                             '   444   00   00 55\n'
                             ' 44  4   00   00 555555\n'
                             '44444444 00   00    5555\n'
                             '   444    00000  555555\n'),
                   'binary': '00110100 00110000 00110101',
                   'reason': 'Method Not Allowed'},
           '408': {'ascii': ('    44    00000   88888\n'
                             '   444   00   00 88   88\n'
                             ' 44  4   00   00  88888\n'
                             '44444444 00   00 88   88\n'
                             '   444    00000   88888\n'),
                   'binary': '00110100 00110000 00111000',
                   'reason': 'Request Timeout'},
           '413': {'ascii': ('    44    1  333333\n'
                             '   444   111    3333\n'
                             ' 44  4    11   3333\n'
                             '44444444  11     333\n'
                             '   444   111 333333\n'),
                   'binary': '00110100 00110001 00110011',
                   'reason': 'Payload Too Large'},
           '500': {'ascii': ('555555   00000   00000\n'
                             '55      00   00 00   00\n'
                             '555555  00   00 00   00\n'
                             '   5555 00   00 00   00\n'
                             '555555   00000   00000\n'),
                   'binary': '00110101 00110000 00110000',
                   'reason': 'Internal Server Error'},
           '503': {'ascii': ('555555   00000  333333\n'
                             '55      00   00    3333\n'
                             '555555  00   00   3333\n'
                             '   5555 00   00     333\n'
                             '555555   00000  333333\n'),
                   'binary': '00110101 00110000 00110011',
                   'reason': 'Service Unavailable'},
           '505': {'ascii': ('555555   00000  555555\n'
                             '55      00   00 55\n'
                             '555555  00   00 555555\n'
                             '   5555 00   00    5555\n'
                             '555555   00000  555555\n'),
                   'binary': '00110101 00110000 00110101',
                   'reason': 'HTTP Version Not Supported'}}


def error(code):
    nt = collections.namedtuple('Status', ('code', 'reason', 'ascii',
                                           'binary', 'html'))
    code = str(code)
    if code not in _status:
        raise KeyError('Unknown status code: {}'.format(code))
    status = _status[code]
    html = ('<html><head><title>{} {}</title></head><body><center><pre>\n{}'
            '\n{}\n</pre></center></body>'
            '</html>'.format(code, status['reason'], status['ascii'],
                             status['binary']))
    return nt(code=int(code), reason=status['reason'], ascii=status['ascii'],
              binary=status['binary'], html=html)
