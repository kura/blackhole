import asyncio
import logging
from unittest import mock

import pytest

from blackhole.child import Child


logging.getLogger('blackhole').addHandler(logging.NullHandler())


def test_initiation():
    Child('', '', [])


def test_start():
    socks = [{'sock': None, 'ctx': None}, {'sock': None, 'ctx': 'abc'}]
    child = Child('', '', socks)
    with mock.patch('asyncio.Task'), \
        mock.patch('blackhole.child.Child.heartbeat'), \
        mock.patch('asyncio.unix_events._UnixSelectorEventLoop.run_forever'), \
            mock.patch('os._exit') as mock_exit:
        child.start()
    assert mock_exit.called is True
