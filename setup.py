import sys

from setup_helpers import require_python, get_version, file_contents
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '--doctest-modules', '--verbose',
            './blackhole', './tests'
        ]
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))


require_python(50659568)
__version__ = get_version('blackhole/__init__.py')

entry_points = {
    'console_scripts': (
        'blackhole = blackhole.application:run',
    )
}

tests_require = [
    'pytest',
    'pytest-asyncio'
]

description = ('Blackhole is an MTA (message transfer agent) that '
               '(figuratively) pipes all mail to /dev/null.')

keywords = ('blackhole', 'mta', 'email')

classifiers = ['Development Status :: 5 - Production/Stable',
               'Environment :: Console',
               'Intended Audience :: Developers',
               'Intended Audience :: Information Technology',
               'Intended Audience :: System Administrators',
               'License :: OSI Approved :: MIT License',
               'Operating System :: POSIX :: Linux',
               'Operating System :: Unix',
               'Programming Language :: Python',
               'Programming Language :: Python :: 3.5',
               'Programming Language :: Python :: 3 :: Only',
               'Topic :: Communications :: Email',
               'Topic :: Communications :: Email :: Mail Transport Agents',
               'Topic :: Education :: Testing',
               'Topic :: Internet',
               'Topic :: Software Development',
               'Topic :: Software Development :: Testing',
               'Topic :: Software Development :: Testing :: Traffic Generation',
               'Topic :: System :: Networking',
               'Topic :: System :: Systems Administration',
               'Topic :: Utilities', ]

setup(name='blackhole',
      version=__version__,
      url='https://blackhole.io/',
      author='Kura',
      author_email='kura@kura.io',
      maintainer='Kura',
      maintainer_email='kura@kura.io',
      description=description,
      long_description=file_contents('README.rst'),
      keywords=', '.join(keywords),
      license=file_contents('LICENSE'),
      platforms=['linux'],
      packages=find_packages(exclude=["*.tests"]),
      install_requires=[],
      tests_require=tests_require,
      cmdclass={'test': PyTest},
      entry_points=entry_points,
      classifiers=classifiers,
      )
