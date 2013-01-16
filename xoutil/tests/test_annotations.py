#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_annotations
#----------------------------------------------------------------------
# Copyright (c) 2012, 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
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
from xoutil.compat import class_types


class Test(unittest.TestCase):
    def test_keywords(self):
        @annotate(a=1, b={1: 4}, args=list, return_annotation=tuple)
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
        def dummy2(a, b):
            return 'Who cares about non-annotated args?'

    def test_mixed_annotations(self):
        from xoutil.compat import _unicode

        @annotate('(a: str, b:_unicode) -> bool', a=_unicode, return_annotation=True)
        def dummy():
            pass

        self.assertIs(dummy.__annotations__.get('a'), _unicode)
        self.assertIs(dummy.__annotations__.get('b'), _unicode)
        self.assertIs(dummy.__annotations__.get('return'), True)

    def test_locals_vars(self):
        args = (1, 2)
        def ns():
            args = (3, 4)
            @annotate('(a: args)')
            def dummy():
                pass
            return dummy

        dummy = ns()
        self.assertEquals(dummy.__annotations__.get('a'), (3, 4))

        @annotate('(a: args)')
        def dummy():
            pass
        self.assertEquals(dummy.__annotations__.get('a'), (1, 2))

    def test_globals(self):
        @annotate('(a: class_types)')
        def dummy():
            pass
        self.assertEquals(dummy.__annotations__['a'], class_types)

    def test_closures_with_locals(self):
        '''
        Tests closures with locals variables.

        In Python 2.7 this behaves as we do (raises a NameError exception)::

            >>> def something():
            ...    args = 1
            ...    l = eval('lambda: args')
            ...    l()

            >>> something()
            Traceback (most recent call last):
                ...
            NameError: global name 'args' is not defined
        '''
        args = (1, 2)
        @annotate('(a: lambda: args)')
        def dummy():
            pass

        with self.assertRaises(NameError):
            dummy.__annotations__.get('a', lambda: None)()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(verbosity=2)
