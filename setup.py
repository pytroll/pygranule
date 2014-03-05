#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Hrobjartur Thorsteinsson

# Author(s):

#   Hrobjartur Thorsteinsson <thorsteinssonh@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


try:
    with open("./README", "r") as fd:
        long_description = fd.read()
except IOError:
    long_description = ""


from setuptools import setup
import imp

version = imp.load_source('pygranule.version', 'pygranule/version.py')

setup(name='pygranule',
      version="v0.1.0",
      description='Satellite granule validating, fetching and scheduling',
      author='Hrobjartur Thorsteinsson',
      author_email='thorsteinssonh@gmail.com',
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: operational meteorology and earth observations",
                   "License :: OSI Approved :: GNU General Public License v3 " +
                   "or later (GPLv3+)",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Scientific/Engineering"],
      url="http://code.google.com/p/get-sat/",
      #download_url="..."
      long_description=long_description,
      license='GPLv3',

      packages = ['pygranule'],

      # Project should use reStructuredText, so ensure that the docutils get
      # installed or upgraded on the target machine
      install_requires=['docutils>=0.3'],
      scripts = [],      
      data_files = [],
      test_suite="nose.collector",
      tests_require=[],

      zip_safe = False
      )
