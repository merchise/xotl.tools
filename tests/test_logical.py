#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_logical
#----------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2015-02-26

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)


import unittest
from xoutil.logical import Logical


class LogicalTests(unittest.TestCase):
    def test_singletons(self):
        from xoutil import Unset
        from xoutil.eight import intern
        foo = 'Un'
        bar = 'set'
        a = Logical('Unset')
        b = Logical(foo + 'set')
        c = Logical('Un' + bar)

        self.assertIs(intern(foo + bar), repr(Unset))
        self.assertIs(repr(a), repr(b))
        self.assertIs(a, Unset)
        self.assertIs(b, Unset)
        self.assertIs(c, Unset)

    def test_equality(self):
        a = Logical('false')
        b = Logical('true', True)
        self.assertEqual(a, False)
        self.assertEqual(b, True)
        self.assertEqual(not b, False)

    def test_parse(self):
        a = Logical('false')
        b = Logical('true', True)
        c = Logical.parse(repr(a))
        self.assertIs(Logical.parse('false'), a)
        self.assertIs(Logical.parse('true'), b)
        self.assertIs(a, c)

    def test_int_compatibility(self):
        a = Logical('false')
        b = Logical('true', True)
        self.assertEqual(a + 1, 1)
        self.assertEqual(b + 1, 2)

    def test_comments(self):
        a = Logical('false')
        value = '%s    # This is a comment' % a
        b = Logical.parse(value)
        self.assertIs(a, b)
