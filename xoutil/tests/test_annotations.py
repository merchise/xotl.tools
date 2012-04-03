#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_annotations
#----------------------------------------------------------------------
# Copyright (c) 2012 Merchise Autrement
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
# Created on Apr 3, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode, 
                        absolute_import)
                        
__docstring_format__ = 'rst'
__author__ = 'manu'

import unittest
from xoutil.annotate import annotate

class Test(unittest.TestCase):
    def test_keywords(self):
        @annotate(a=1, b={1:4}, args=list, return_annotation=tuple)
        def dummy():
            pass
        
        self.assertEqual(dummy.__annotations__.get('a', None), 1)
        self.assertEqual(dummy.__annotations__.get('b', None), {1: 4})
        self.assertEqual(dummy.__annotations__.get('args', None), list)
        self.assertEqual(dummy.__annotations__.get('return', None), tuple)

        
    def test_signature(self):
        @annotate('(a: 1, b: {1: 4}, *args: list, **kwargs: dict) -> tuple')
        def dummy():
            pass
        
        self.assertEqual(dummy.__annotations__.get('a', None), 1)
        self.assertEqual(dummy.__annotations__.get('b', None), {1: 4})
        self.assertEqual(dummy.__annotations__.get('args', None), list)
        self.assertEqual(dummy.__annotations__.get('kwargs', None), dict)
        self.assertEqual(dummy.__annotations__.get('return', None), tuple)
        
    
    def test_invalid_nonsense_signature(self):
        with self.assertRaises(SyntaxError):
            @annotate('(a, b) -> list')
            def dummy(a, b):
                pass
            
        # But the following is ok
        @annotate('() -> list')
        def dummy(a, b):
            return 'Who cares about non-annotated args?'
        
        
    def test_mixed_annotations(self):
        @annotate('(a: str, b:unicode) -> bool', a=unicode, return_annotation=True)
        def dummy():
            pass
        
        self.assertIs(dummy.__annotations__.get('a'), unicode)
        self.assertIs(dummy.__annotations__.get('b'), unicode)
        self.assertIs(dummy.__annotations__.get('return'), True)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(verbosity=2)