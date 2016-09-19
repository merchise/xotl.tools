#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_symbols
#----------------------------------------------------------------------
# Copyright (c) 2015, 2016 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2015-02-26

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


import unittest
from xoutil.symbols import boolean


class BooleanTests(unittest.TestCase):
    def test_singletons(self):
        from xoutil import Unset
        from xoutil.eight import intern
        foo = 'Un'
        bar = 'set'
        a = boolean('Unset')
        b = boolean(foo + 'set')
        c = boolean('Un' + bar)

        # self.assertIs(intern(foo + bar), repr(Unset))
        # above started to fail in PyPy, changed to next.
        self.assertIs(intern(foo + bar), intern(repr(Unset)))
        self.assertIs(repr(a), repr(b))
        self.assertIs(a, Unset)
        self.assertIs(b, Unset)
        self.assertIs(c, Unset)

    def test_equality(self):
        a = boolean('false')
        b = boolean('true', True)
        self.assertEqual(a, False)
        self.assertEqual(b, True)
        self.assertEqual(not b, False)

    def test_parse(self):
        a = boolean('false')
        b = boolean('true', True)
        c = boolean.parse(repr(a))
        self.assertIs(boolean.parse('false'), a)
        self.assertIs(boolean.parse('true'), b)
        self.assertIs(a, c)

    def test_int_compatibility(self):
        a = boolean('false')
        b = boolean('true', True)
        self.assertEqual(a + 1, 1)
        self.assertEqual(b + 1, 2)

    def test_comments(self):
        a = boolean('false')
        value = '%s    # This is a comment' % a
        b = boolean.parse(value)
        self.assertIs(a, b)
