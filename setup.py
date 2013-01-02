import os
import glob
from setuptools import setup
from setuptools import find_packages

setup(name='blackhole',
      version="1.3.1",
      url='http://blackhole.io/',
      author="Kura",
      author_email="kura@kura.io",
      description="Tornado powered MTA for accepting all incoming emails without any disk I/O, although no messages actually ever get delivered. Mainly for testing huge send rates, for making sure developers don't accidentally send emails to real users, email integration testing and things like that.",
      long_description=open("README.rst").read(),
      license='BSD',
      platforms=['linux'],
      packages=find_packages(exclude=["*.tests"]),
      install_requires=[
          'tornado==2.3',
          'setproctitle==1.1.6',
          'deiman==0.1',
      ],
      scripts=[
          'blackhole/bin/blackhole',
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Operating System :: POSIX',
          'Operating System :: POSIX :: Linux',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Topic :: Internet',
          'Topic :: Utilities',
      ],
      zip_safe=False,
      )
