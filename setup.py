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

Blackhole is built on top of asyncio and utilises `async` and `await`
statements on available in Python 3.5 and above.

While Blackhole is an MTA (mail transport agent), none of the actions
performed of SMTP or SMTPS are actually processed and no email or sent or
delivered.
"""


from setup_helpers import require_python, get_version, long_description
from setuptools import setup, find_packages


require_python(50659568)
__version__ = get_version('blackhole/__init__.py')

desc = """Blackhole is an email MTA that pipes all mail to /dev/null.

Blackhole is built on top of asyncio and utilises `async` and `await`
statements on available in Python 3.5 and above.

While Blackhole is an MTA (mail transport agent), none of the actions
performed of SMTP or SMTPS are actually processed and no email or sent or
delivered."""


entry_points = {
    'console_scripts': [
        'blackhole = blackhole.application:run',
    ]
}


setup(name='blackhole',
      version=__version__,
      url='https://blackhole.io/',
      author='Kura',
      author_email='kura@kura.io',
      maintainer='Kura',
      maintainer_email='kura@kura.io',
      description=desc,
      long_description=long_description('README.rst'),
      license='MIT',
      platforms=['linux'],
      packages=find_packages(exclude=["*.tests"]),
      install_requires=[],
      entry_points=entry_points,
      classifiers=[
          'Programming Language :: Python :: 3.5',
          'Topic :: Internet',
          'Topic :: Utilities',
          'Topic :: Communications :: Email',
          'Topic :: Communications :: Email :: Mail Transport Agents',
          'Topic :: Software Development :: Testing',
          'Topic :: Software Development :: Testing :: Traffic Generation',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
      ],
      zip_safe=True,
      )
