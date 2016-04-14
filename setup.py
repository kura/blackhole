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


import sys

from setuptools import setup
from setuptools import find_packages


if sys.version_info < (3, 5):
    print("blackhole requires Python 3.5 or greater")
    sys.exit(1)

version = __import__('blackhole').__version__

desc = """Needs changing"""

entry_points = {
    'console_scripts': [
        'blackhole = blackhole.application:run',
    ]
}


setup(name='blackhole',
      version=version,
      url='http://blackhole.io/',
      download_url='https://github.com/kura/blackhole/archive/%s.zip' % version,
      author="Kura",
      author_email="kura@kura.io",
      maintainer="Kura",
      maintainer_email="kura@kura.io",
      description=desc,
      long_description=open("README.rst").read(),
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
