# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_fs
#----------------------------------------------------------------------
# Copyright (c) 2011 Medardo Rodríguez
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on Feb 15, 2012

'Tests for xoutil.fs module'

import os
import sys
import unittest

# Makes sure our package is always importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import xoutil.fs

class TestFs(unittest.TestCase):
    def setUp(self):
        # Makes all names predictable
        self.previous_dir = os.getcwd()
        os.chdir('/tmp')

    def tearDown(self):
        os.chdir(self.previous_dir)



if __name__ == '__main__':
    unittest.main()
