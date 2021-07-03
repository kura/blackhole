# -*- coding: utf-8 -*-

# (The MIT License)
#
# Copyright (c) 2013-2021 Kura
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


import asyncio
from unittest import mock

import pytest

from blackhole.config import Config
from blackhole.worker import Worker


from ._utils import (  # noqa: F401; isort:skip
    Args,
    cleandir,
    create_config,
    create_file,
    reset,
)


@pytest.mark.usefixtures("reset", "cleandir")
@pytest.mark.asyncio
@pytest.mark.slow
async def test_start_stop(event_loop):
    worker = Worker(1, [], loop=event_loop)
    assert worker._started is True
    await asyncio.sleep(10)
    worker.stop()
    assert worker._started is False


@pytest.mark.usefixtures("reset", "cleandir")
def test_child_start_setgid_fails_invalid_group(event_loop):
    cfile = create_config(
        ("user=fgqewgreghrehgerhehw", "group=fgqewgreghrehgerhehw"),
    )
    Config(cfile).load()
    with mock.patch("os.pipe", return_value=("", "")), mock.patch(
        "os.fork",
        return_value=False,
    ), mock.patch("os.close"), mock.patch(
        "os.setgid",
        side_effect=KeyError,
    ), pytest.raises(
        SystemExit,
    ) as exc:
        Worker([], [], loop=event_loop)
    assert exc.value.code == 64


@pytest.mark.usefixtures("reset", "cleandir")
def test_child_start_setgid_fails_permissions(event_loop):
    cfile = create_config(
        ("user=fgqewgreghrehgerhehw", "group=fgqewgreghrehgerhehw"),
    )
    Config(cfile).load()
    with mock.patch("os.pipe", return_value=("", "")), mock.patch(
        "os.fork",
        return_value=False,
    ), mock.patch("os.close"), mock.patch(
        "os.setgid",
        side_effect=PermissionError,
    ), pytest.raises(
        SystemExit,
    ) as exc:
        Worker([], [], loop=event_loop)
    assert exc.value.code == 64


@pytest.mark.usefixtures("reset", "cleandir")
def test_child_start_setuid_fails_invalid_user(event_loop):
    cfile = create_config(
        ("user=fgqewgreghrehgerhehw", "group=fgqewgreghrehgerhehw"),
    )
    Config(cfile).load()
    with mock.patch("os.pipe", return_value=("", "")), mock.patch(
        "os.fork",
        return_value=False,
    ), mock.patch("os.close"), mock.patch(
        "os.setuid",
        side_effect=KeyError,
    ), pytest.raises(
        SystemExit,
    ) as exc:
        Worker([], [], loop=event_loop)
    assert exc.value.code == 64


@pytest.mark.usefixtures("reset", "cleandir")
def test_child_start_setuid_fails_permissions(event_loop):
    cfile = create_config(
        ("user=fgqewgreghrehgerhehw", "group=fgqewgreghrehgerhehw"),
    )
    Config(cfile).load()
    with mock.patch("os.pipe", return_value=("", "")), mock.patch(
        "os.fork",
        return_value=False,
    ), mock.patch("os.close"), mock.patch(
        "os.setuid",
        side_effect=PermissionError,
    ), pytest.raises(
        SystemExit,
    ) as exc:
        Worker([], [], loop=event_loop)
    assert exc.value.code == 64
