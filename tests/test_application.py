# -*- coding: utf-8 -*-

# (The MIT License)
#
# Copyright (c) 2013-2020 Kura
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


import os
from unittest import mock

import pytest

from blackhole.application import blackhole_config, run
from blackhole.config import Config
from blackhole.exceptions import (
    BlackholeRuntimeException,
    ConfigException,
    DaemonException,
)


from ._utils import (  # noqa: F401; isort:skip
    Args,
    cleandir,
    create_config,
    create_file,
    reset,
)


@pytest.mark.usefixtures("reset", "cleandir")
def test_run_test():
    cfile = create_config(("",))
    with mock.patch("sys.argv", ["blackhole", "-t", "-c", cfile]), mock.patch(
        "blackhole.config.Config.test_port", return_value=True
    ), mock.patch(
        "blackhole.config.Config.test_pidfile", return_value=True
    ), pytest.raises(
        SystemExit
    ) as exc:
        run()
    assert exc.value.code == 0


@pytest.mark.usefixtures("reset", "cleandir")
def test_run_test_fails():
    cfile = create_config(("listen=127.0.0.1:0",))
    with mock.patch(
        "sys.argv", ["blackhole", "-t", "-c", cfile]
    ), pytest.raises(SystemExit) as exc:
        run()
    assert exc.value.code == 64


@pytest.mark.usefixtures("reset", "cleandir")
def test_run_load_test_fails():
    cfile = create_config(("listen=127.0.0.1:0",))
    with mock.patch("sys.argv", ["blackhole", "-t", "-c", cfile]), mock.patch(
        "blackhole.config.Config.test", side_effect=ConfigException()
    ), pytest.raises(SystemExit) as exc:
        run()
    assert exc.value.code == 64


@pytest.mark.usefixtures("reset", "cleandir")
def test_run_foreground():
    pidfile = os.path.join(os.getcwd(), "blackhole-test.pid")
    cfile = create_config(
        ("listen=127.0.0.1:9000", "pidfile={}".format(pidfile))
    )
    c = Config(cfile).load()

    with mock.patch("sys.argv", ["-c {}".format(cfile)]), mock.patch(
        "blackhole.config.Config.test", return_value=c
    ), mock.patch("blackhole.config.warn_options"), mock.patch(
        "atexit.register"
    ), mock.patch(
        "os.chown"
    ), mock.patch(
        "blackhole.supervisor.Supervisor.generate_servers"
    ), mock.patch(
        "blackhole.control.pid_permissions"
    ), mock.patch(
        "blackhole.control.setgid"
    ), mock.patch(
        "blackhole.control.setuid"
    ), mock.patch(
        "blackhole.supervisor.Supervisor.run"
    ), pytest.raises(
        SystemExit
    ) as exc:
        run()
    assert exc.value.code == 0


@pytest.mark.usefixtures("reset", "cleandir")
def test_run_foreground_pid_error():
    pidfile = os.path.join(os.getcwd(), "blackhole-test.pid")
    cfile = create_config(
        ("listen=127.0.0.1:9000", "pidfile={}".format(pidfile))
    )
    c = Config(cfile).load()

    with mock.patch("sys.argv", ["-c {}".format(cfile)]), mock.patch(
        "blackhole.config.Config.test", return_value=c
    ), mock.patch("blackhole.config.warn_options"), mock.patch(
        "os.getpid", return_value=1234
    ), mock.patch(
        "atexit.register", side_effect=DaemonException
    ), pytest.raises(
        SystemExit
    ) as exc:
        run()
    assert exc.value.code == 64


@pytest.mark.usefixtures("reset", "cleandir")
def test_run_foreground_socket_error():
    pidfile = os.path.join(os.getcwd(), "blackhole-test.pid")
    cfile = create_config(
        ("listen=127.0.0.1:9000", "pidfile={}".format(pidfile))
    )
    c = Config(cfile).load()

    with mock.patch("sys.argv", ["-c {}".format(cfile)]), mock.patch(
        "blackhole.config.Config.test", return_value=c
    ), mock.patch("blackhole.config.warn_options"), mock.patch(
        "atexit.register"
    ), mock.patch(
        "blackhole.supervisor.Supervisor.close_socks"
    ), mock.patch(
        "blackhole.supervisor.Supervisor.generate_servers",
        side_effect=BlackholeRuntimeException,
    ), pytest.raises(
        SystemExit
    ) as exc:
        run()
    assert exc.value.code == 77


@pytest.mark.usefixtures("reset", "cleandir")
def test_run_background():
    pidfile = os.path.join(os.getcwd(), "blackhole-test.pid")
    cfile = create_config(
        ("listen=127.0.0.1:9000", "pidfile={}".format(pidfile))
    )
    c = Config(cfile).load()

    with mock.patch("sys.argv", ["-c {}".format(cfile), "-b"]), mock.patch(
        "blackhole.config.Config.test", return_value=c
    ), mock.patch("blackhole.config.warn_options"), mock.patch(
        "atexit.register"
    ), mock.patch(
        "os.chown"
    ), mock.patch(
        "blackhole.supervisor.Supervisor.generate_servers"
    ), mock.patch(
        "blackhole.daemon.Daemon.daemonize"
    ), mock.patch(
        "blackhole.control.pid_permissions"
    ), mock.patch(
        "blackhole.control.setgid"
    ), mock.patch(
        "blackhole.control.setuid"
    ), mock.patch(
        "blackhole.supervisor.Supervisor.run"
    ), pytest.raises(
        SystemExit
    ) as exc:
        run()
    assert exc.value.code == 0


@pytest.mark.usefixtures("reset", "cleandir")
def test_run_daemon_daemonize_error():
    pidfile = os.path.join(os.getcwd(), "blackhole-test.pid")
    cfile = create_config(
        ("listen=127.0.0.1:9000", "pidfile={}".format(pidfile))
    )
    c = Config(cfile).load()

    with mock.patch("sys.argv", ["-c {}".format(cfile), "-b"]), mock.patch(
        "blackhole.application.Config.test", return_value=c
    ), mock.patch("blackhole.config.warn_options"), mock.patch(
        "atexit.register"
    ), mock.patch(
        "os.chown"
    ), mock.patch(
        "blackhole.supervisor.Supervisor.generate_servers"
    ), mock.patch(
        "os.fork", side_effect=OSError
    ), mock.patch(
        "blackhole.supervisor.Supervisor." "close_socks"
    ) as mock_close, pytest.raises(
        SystemExit
    ) as exc:
        run()
    assert exc.value.code == 77
    assert mock_close.called is True


@pytest.mark.usefixtures("reset", "cleandir")
def test_blackhole_config():
    with pytest.raises(SystemExit) as exc:
        blackhole_config()
    assert exc.value.code == 0
