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

"""Setup file."""

import io
import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


assert sys.version_info >= (3, 6, 0), "blackhole requires Python 3.6+"


class PyTest(TestCommand):
    """Test command."""

    def finalize_options(self):
        """Build options."""
        TestCommand.finalize_options(self)
        self.test_args = ["--pylama", "-q", "./blackhole", "./tests"]
        self.test_suite = True

    def run_tests(self):
        """Run ze tests."""
        import pytest

        sys.exit(pytest.main(self.test_args))


def include_file(filename):
    """Include contents of specified file."""
    fpath = os.path.join(os.path.dirname(__file__), filename)
    with io.open(fpath, encoding="utf-8") as f:
        c = f.read()
    return c


def get_version(filepath):
    """Return program version."""
    for line in include_file(filepath).split("\n"):
        if line.startswith("__version__"):
            _, vers = line.split("=")
            return vers.strip().replace('"', "").replace("'", "")


__version__ = get_version("blackhole/__init__.py")

entry_points = {
    "console_scripts": (
        "blackhole = blackhole.application:run",
        "blackhole_config = blackhole.application:blackhole_config",
    )
}

extras_require = {
    "setproctitle": ["setproctitle"],
    "uvloop": ["uvloop"],
    "docs": ["sphinx", "guzzle_sphinx_theme"],
    "tests": [
        "coverage",
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-clarity",
    ],
}

extras_require["dev"] = (
    extras_require["docs"] + extras_require["tests"] + ["tox", "pre-commit"]
)

description = (
    "Blackhole is an MTA (message transfer agent) that "
    "(figuratively) pipes all mail to /dev/null."
)

keywords = ("blackhole", "asyncio", "smtp", "mta", "email")

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: POSIX :: Linux",
    "Operating System :: Unix",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Topic :: Communications :: Email",
    "Topic :: Communications :: Email :: Mail Transport Agents",
    "Topic :: Education :: Testing",
    "Topic :: Internet",
    "Topic :: Software Development",
    "Topic :: Software Development :: Testing",
    "Topic :: Software Development :: Testing :: Traffic Generation",
    "Topic :: System :: Networking",
    "Topic :: System :: Systems Administration",
    "Topic :: Utilities",
]

setup(
    author="Kura",
    author_email="kura@kura.gg",
    classifiers=classifiers,
    cmdclass={"test": PyTest},
    description=description,
    entry_points=entry_points,
    extras_require=extras_require,
    install_requires=[],
    keywords=" ".join(keywords),
    license="MIT",
    long_description="\n" + include_file("README.rst"),
    maintainer="Kura",
    maintainer_email="kura@kura.gg",
    name="blackhole",
    packages=find_packages(exclude=("tests",)),
    platforms=["linux"],
    url="https://kura.github.io/blackhole/",
    version=__version__,
    zip_safe=False,  # this is probably not correct, but I've never tested it.
)
