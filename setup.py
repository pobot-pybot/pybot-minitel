#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import textwrap

setup(name='pynitel',
      version='1.0',
      description='Minitel library',
      license='LGPL',
      author='Eric Pascual',
      author_email='eric@pobot.org',
      url='http://www.pobot.org',
      packages=find_packages("src"),
      package_dir={'': 'src'}
      )
