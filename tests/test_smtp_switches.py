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

# pylama:skip=1

import unittest

import pytest

from blackhole.config import Config
from blackhole.smtp import Smtp

from ._utils import (Args, cleandir, create_config, create_file, reset)


@pytest.mark.usefixtures('reset', 'cleandir')
class TestHeadersSwitchDisabled(unittest.TestCase):

    def test_headers_disabled(self):
        cfile = create_config(('dynamic_switch=false', ))
        Config(cfile).load()
        smtp = Smtp([])
        assert smtp.mode == 'accept'
        smtp.process_header('x-blackhole-mode: bounce')
        assert smtp.mode == 'accept'

    def test_headers_enabled(self):
        cfile = create_config(('dynamic_switch=true', ))
        Config(cfile).load()
        smtp = Smtp([])
        assert smtp.mode == 'accept'
        smtp.process_header('x-blackhole-mode: bounce')
        assert smtp.mode == 'bounce'

    def test_headers_default(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        assert smtp.mode == 'accept'
        smtp.process_header('x-blackhole-mode: bounce')
        assert smtp.mode == 'bounce'


@pytest.mark.usefixtures('reset', 'cleandir')
class TestDynamicSwitchDisabledByFlags(unittest.TestCase):

    def test_mode(self):
        smtp = Smtp([])
        smtp.mode = 'accept'
        smtp._flags = {'mode': 'bounce'}
        assert smtp.mode == 'bounce'

    def test_delay(self):
        smtp = Smtp([])
        smtp.delay = '30'
        smtp._flags = {'delay': 20}
        assert smtp.delay == 20

    def test_delay_range(self):
        smtp = Smtp([])
        smtp.delay = '30'
        smtp._flags = {'delay': ['10', '20']}
        assert smtp.delay in (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)

    def test_delay_and_mode(self):
        smtp = Smtp([])
        smtp.delay = '30'
        smtp.mode = 'accept'
        smtp._flags = {'delay': '20', 'mode': 'bounce'}
        assert smtp.delay == 20
        assert smtp.mode == 'bounce'

    def test_delay_range_and_mode(self):
        smtp = Smtp([])
        smtp.delay = '30'
        smtp.mode = 'accept'
        smtp._flags = {'delay': ['10', '20'], 'mode': 'bounce'}
        assert smtp.delay in (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)
        assert smtp.mode == 'bounce'


@pytest.mark.usefixtures('reset', 'cleandir')
class TestProcessHeaders(unittest.TestCase):

    def test_valid_mode_header(self):
        smtp = Smtp([])
        assert smtp.mode == 'accept'
        smtp.process_header('x-blackhole-mode: bounce')
        assert smtp.mode == 'bounce'

    def test_invalid_mode_header(self):
        smtp = Smtp([])
        assert smtp.mode == 'accept'
        smtp.process_header('x-blackhole-mode: help')
        assert smtp.mode == 'accept'

    def test_invalid_mode_header2(self):
        smtp = Smtp([])
        assert smtp.mode == 'accept'
        smtp.process_header('x-some-mode: bounce')
        assert smtp.mode == 'accept'

    def test_valid_single_delay(self):
        smtp = Smtp([])
        assert smtp.delay is None
        smtp.process_header('x-blackhole-delay: 30')
        assert smtp.delay is 30

    def test_invalid_single_delay(self):
        smtp = Smtp([])
        assert smtp.delay is None
        smtp.process_header('x-blackhole-delay: abc')
        assert smtp.delay is None

    def test_valid_range_delay(self):
        smtp = Smtp([])
        assert smtp.delay is None
        smtp.process_header('x-blackhole-delay: 5, 10')
        assert smtp.delay in [5, 6, 7, 8, 9, 10]

    def test_invalid_range_delay(self):
        smtp = Smtp([])
        assert smtp.delay is None
        smtp.process_header('x-blackhole-delay: abc, def')
        assert smtp.delay is None


@pytest.mark.usefixtures('reset', 'cleandir')
class TestModeSwitch(unittest.TestCase):

    def test_mode_default(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        assert smtp.mode == 'accept'

    def test_mode_invalid(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.mode = 'kura'
        assert smtp.mode == 'accept'

    def test_mode_valid(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.mode = 'bounce'
        assert smtp.mode == 'bounce'

    def test_mode_valid_overrides_config(self):
        cfile = create_config(('mode=bounce', ))
        Config(cfile).load()
        smtp = Smtp([])
        assert smtp.mode == 'bounce'
        smtp.mode = 'accept'
        assert smtp.mode == 'accept'


@pytest.mark.usefixtures('reset', 'cleandir')
class TestDelaySwitch(unittest.TestCase):

    def test_delay_not_enabled_or_set(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        assert smtp.delay is None

    def test_delay_from_config(self):
        cfile = create_config(('delay=30', ))
        Config(cfile).load()
        smtp = Smtp([])
        assert smtp.delay is 30

    def test_delay_switch_overrides_config_single(self):
        cfile = create_config(('delay=30', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.delay = '60'
        assert smtp.delay is 60
        assert smtp.config.delay is 30

    def test_delay_switch_range_overrides_config(self):
        cfile = create_config(('delay=30', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.delay = '40, 45'
        assert smtp.delay in [x for x in range(40, 46)]
        assert smtp.config.delay is 30

    def test_delay_switch_invalid_single_value_no_config(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.delay = 'fifteen'
        assert smtp.delay is None

    def test_delay_switch_invalid_single_value_config_60(self):
        cfile = create_config(('delay=30', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.delay = 'fifteen'
        assert smtp.delay is 30

    def test_delay_switch_invalid_single_negative_value(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.delay = '-10'
        assert smtp.delay is None

    def test_delay_switch_not_above_max(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.delay = '90'
        assert smtp.delay is 60

    def test_delay_switch_invalid_range_value_no_config(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.delay = 'fifteen, eighteen'
        assert smtp.delay is None

    def test_delay_switch_invalid_min_range_value_no_config(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.delay = 'fifteen, 18'
        assert smtp.delay is None

    def test_delay_switch_invalid_max_range_value_no_config(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.delay = '15, eighteen'
        assert smtp.delay is None

    def test_delay_switch_invalid_range_negative_min_value(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.delay = '-10, 10'
        assert smtp.delay is None

    def test_delay_switch_invalid_range_negative_max_value(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.delay = '1, -10'
        assert smtp.delay is None

    def test_delay_switch_invalid_range_negatives(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.delay = '-10, -1'
        assert smtp.delay is None

    def test_delay_switch_range_min_higher_than_max(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.delay = '20, 10'
        assert smtp.delay is None

    def test_delay_switch_range_max_higher_than_60(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.delay = '59, 70'
        assert smtp.delay in [59, 60]

    def test_delay_switch_more_than_2(self):
        cfile = create_config(('', ))
        Config(cfile).load()
        smtp = Smtp([])
        smtp.delay = '1, 2, 3'
        assert smtp.delay is None
