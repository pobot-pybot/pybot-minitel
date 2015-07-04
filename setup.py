#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='pybot_minitel',
      namespace_packages=['pybot'],
      version='1.0',
      description='Minitel library',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering',
          'Programming Language :: Python :: 2.7',
          'Environment :: No Input/Output (Daemon)',
          'Environment :: Raspberry Pi',
          'Operating System :: POSIX :: Linux',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Natural Language :: English'
      ],
      license='LGPL',
      author='Eric Pascual',
      author_email='eric@pobot.org',
      url='http://www.pobot.org',
      packages=find_packages("src"),
      package_dir={'': 'src'},
      package_data={
          'pybot_minitel': ['demos/data/form_def.json', 'demos/data/img/*.png', 'demos/data/img/*.txt']
      },
      entry_points={
          'console_scripts': [
              'pybot_minitel_demo = pybot_minitel.demos:main'
          ]
      }
)
