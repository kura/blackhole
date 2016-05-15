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
Blackhole is an email MTA that pipes all mail to /dev/null.

Blackhole is built on top of asyncio and utilises :any:`async def` and
:any:`await` statements on available in Python 3.5 and above.

While Blackhole is an MTA (mail transport agent), none of the actions
performed of SMTP or SMTPS are actually processed and no email or sent or
delivered.
"""

from .application import *
from .child import *
from .config import *
from .control import *
from .daemon import *
from .exceptions import *
from .logs import *
from .protocols import *
from .smtp import *
from .streams import *
from .supervisor import *
from .utils import *
from .worker import *


__author__ = 'Kura'
__copyright__ = 'None'
__credits__ = ('Kura', )
__license__ = 'MIT'
__version__ = '2.1.4'
__maintainer__ = 'Kura'
__email__ = 'kura@kura.io'
__status__ = 'Stable'


__all__ = (application.__all__ +
           child.__all__ +
           config.__all__ +
           control.__all__ +
           daemon.__all__ +
           exceptions.__all__ +
           logs.__all__ +
           protocols.__all__ +
           smtp.__all__ +
           streams.__all__ +
           supervisor.__all__ +
           utils.__all__ +
           worker.__all__)
