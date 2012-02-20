#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_decorators
#----------------------------------------------------------------------
# Copyright (c) 2011 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
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
# Created on Nov 8, 2011

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

__docstring_format__ = 'rst'
__author__ = 'manu'


import unittest
from xoutil.pep3124 import overload, OverloadError

class TestBasicOverloading(unittest.TestCase):
    def setUp(self):
        overload._cleanup()  # In order to start fresh every time.

        @overload(int)
        def tab(a):
            return a

        @overload(str)
        def tab(a):
            return len(a)

        @overload(unicode)
        def tab(a):
            return len(a)

        @overload(str, int)
        def tab(strarg, intarg):
            return len(strarg * intarg)

        @overload(unicode, int)
        def tab(strarg, intarg):
            return len(strarg * intarg)

        self.tab = tab


    def test_int(self):
        self.assertEqual(1, self.tab(1))


    def test_uni(self):
        self.assertEqual(5, self.tab('means'))


    def test_bytes(self):
        self.assertEqual(6, self.tab(b'árbol'))


    def test_any_int(self):
        self.assertEqual(12, self.tab(b'árbol', 2))


    def test_conflict(self):
        'Raises an exception when a new definition conflicts with a previous one'
        with self.assertRaises(OverloadError):
            @overload(str)
            def tab(a):
                pass

if __name__ == '__main__':
    unittest.main(verbosity=2)
