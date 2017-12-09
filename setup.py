# -*- coding: utf-8 -*-

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

"""Setup file."""

from setuptools import find_packages, setup

from setup_helpers import (PyTest, get_version, include_file,
                           require_python)


require_python(50725104)
__version__ = get_version('blackhole/__init__.py')

entry_points = {
    'console_scripts': (
        'blackhole = blackhole.application:run',
        'blackhole_config = blackhole.application:blackhole_config',
    )
}

extras_require = {
    'setproctitle': ['setproctitle', ],
    'uvloop': ['uvloop', ],
}

tests_require = ('codecov',
                 'guzzle_sphinx_theme',
                 'isort',
                 'pyannotate',
                 'pycodestyle',
                 'pydocstyle',
                 'pyflakes',
                 'pylama',
                 'pytest',
                 'pytest-asyncio',
                 'pytest-cov',
                 'radon',
                 'sphinx', )

description = ('Blackhole is an MTA (message transfer agent) that '
               '(figuratively) pipes all mail to /dev/null.')

keywords = ('blackhole', 'asyncio', 'smtp', 'mta', 'email')

classifiers = ['Development Status :: 5 - Production/Stable',
               'Environment :: Console',
               'Intended Audience :: Developers',
               'Intended Audience :: Information Technology',
               'Intended Audience :: System Administrators',
               'License :: OSI Approved :: MIT License',
               'Operating System :: POSIX :: Linux',
               'Operating System :: Unix',
               'Programming Language :: Python',
               'Programming Language :: Python :: 3.6',
               'Programming Language :: Python :: 3 :: Only',
               'Topic :: Communications :: Email',
               'Topic :: Communications :: Email :: Mail Transport Agents',
               'Topic :: Education :: Testing',
               'Topic :: Internet',
               'Topic :: Software Development',
               'Topic :: Software Development :: Testing',
               ('Topic :: Software Development :: Testing :: '
                'Traffic Generation'),
               'Topic :: System :: Networking',
               'Topic :: System :: Systems Administration',
               'Topic :: Utilities', ]

setup(
    author='Kura',
    author_email='kura@kura.io',
    classifiers=classifiers,
    cmdclass={'test': PyTest},
    description=description,
    entry_points=entry_points,
    extras_require=extras_require,
    install_requires=[],
    keywords=' '.join(keywords),
    license='MIT',
    long_description='\n' + include_file('README.rst'),
    maintainer='Kura',
    maintainer_email='kura@kura.io',
    name='blackhole',
    packages=find_packages(exclude=('tests',)),
    platforms=['linux'],
    tests_require=tests_require,
    url='https://blackhole.io/',
    version=__version__,
    zip_safe=False,  # this is probably not correct, but I've never tested it.
)
