import os
import glob
from setuptools import setup
from setuptools import find_packages

setup(name='blackhole',
      version="1.2.4",
      url='http://blackhole.io/',
      author="Kura",
      author_email="kura@kura.io",
      description="An asynchronous Python-powered MTA",
      long_description=file(
          os.path.join(
              os.path.dirname(__file__),
              'README.rst'
          )
      ).read(),
      license='BSD',
      platforms=['linux'],
      packages=find_packages(exclude=["*.tests"]),
      install_requires=file(os.path.join(os.path.dirname(__file__),
                                         'requirements.txt')).read(),
      scripts=[
          'blackhole/bin/blackhole',
      ],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: Internet',
          'Topic :: Utilities',
      ],
      zip_safe=False,
      )
