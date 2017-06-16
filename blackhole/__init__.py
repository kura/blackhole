# (The MIT License)
#
# Copyright (c) 2013-2017 Kura
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
Blackhole is an email MTA that pipes all mail to /dev/null.

Blackhole is built on top of asyncio and utilises :py:obj:`async def` and
:py:obj:`await` statements on available in Python 3.5 and above.

While Blackhole is an MTA (mail transport agent), none of the actions
performed of SMTP or SMTPS are actually processed and no email or sent or
delivered.
"""

from .application import __all__ as __application_all__
from .child import __all__ as __child_all__
from .config import __all__ as __config_all__
from .control import __all__ as __control_all__
from .daemon import __all__ as __daemon_all__
from .exceptions import __all__ as __exceptions_all__
from .logs import __all__ as __logs_all__
from .protocols import __all__ as __protocols_all__
from .smtp import __all__ as __smtp_all__
from .streams import __all__ as __streams_all__
from .supervisor import __all__ as __supervisor_all__
from .utils import __all__ as __utils_all__
from .worker import __all__ as __worker_all__


__author__ = 'Kura'
__copyright__ = 'None'
__credits__ = ('Kura', )
__license__ = 'MIT'
__version__ = '2.1.8'
__maintainer__ = 'Kura'
__email__ = 'kura@kura.io'
__status__ = 'Stable'


__all__ = (__application_all__ +
           __child_all__ +
           __config_all__ +
           __control_all__ +
           __daemon_all__ +
           __exceptions_all__ +
           __logs_all__ +
           __protocols_all__ +
           __smtp_all__ +
           __streams_all__ +
           __supervisor_all__ +
           __utils_all__ +
           __worker_all__)
"""Tuple all the things."""
