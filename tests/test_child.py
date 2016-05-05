import logging
from unittest import mock

from blackhole.child import Child


logging.getLogger('blackhole').addHandler(logging.NullHandler())


def test_initiation():
    Child('', '', '')


def test_start():
    socks = [{'sock': None, 'ctx': None}, {'sock': None, 'ctx': 'abc'}]
    child = Child('', '', socks)
    with mock.patch('asyncio.unix_events._UnixSelectorEventLoop.'
                    'create_server') as mock_create, \
        mock.patch('asyncio.unix_events._UnixSelectorEventLoop.'
                   'run_until_complete') as mock_run, \
        mock.patch('asyncio.async'), \
        mock.patch('asyncio.unix_events._UnixSelectorEventLoop.run_forever'), \
            mock.patch('os._exit') as mock_exit:
        child.start()
    assert mock_create.call_count is 2
    assert mock_run.call_count is 2
    assert mock_exit.called is True
