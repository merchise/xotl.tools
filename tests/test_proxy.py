#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xotl.models.ql.tests.test_expressions
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on May 25, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

import unittest

from xoutil.context import context
from xoutil.proxy import proxify, UNPROXIFING_CONTEXT, unboxed


class Foobar(object):
    def hi(self):
        print('Hello from ', self)


class HackedHi(object):
    def hi(self):
        return self


class Addition(object):
    def __add__(self, other):
        return self
    __radd__ = __add__


class UnproxifingAddition(object):
    def __add__(self, other):
        return self.target
    __radd__ = __add__


class TestProxy(unittest.TestCase):
    def test_proxy(self):
        @proxify
        class Proxified(object):
            behaves = [HackedHi, Addition]

            def __init__(self, target):
                self.target = target


        x1 = Foobar()
        y = Proxified(x1)
        r = y.hi()
        self.assertIs(r, y)

        self.assertIs(r + 1, r)
        self.assertIs(1 + r, r)

        self.assertEqual(r + 1, r)
        self.assertEqual(1 + r, r)

        with self.assertRaises(AttributeError):
            _q = r / 1

    def test_unproxifing_addition(self):
        @proxify
        class Proxified(object):
            def __init__(self, target):
                self.target = target
                self.behaves = [UnproxifingAddition]

        x1 = Foobar()
        y = Proxified(x1)
        self.assertEqual(x1, y + 1)

    def test_explicit_unproxification(self):
        @proxify
        class Proxified(object):
            def __init__(self, target):
                self.target = target
                self.behaves = [HackedHi, Addition]

        foo = Foobar()
        proxy = Proxified(foo)
        with context(UNPROXIFING_CONTEXT):
            target = proxy.target
        self.assertIs(foo, target)

    def test_unboxed(self):
        class X(object):
            l = [1, 2, 4]

        @proxify
        class Proxified(object):
            def __init__(self, target):
                self.target = target
                self.l = [1, 3]

        x = X()
        p = Proxified(x)
        unboxed(p, 'l') << 234
        self.assertEqual([1, 3, 234], unboxed(p).l)
        self.assertEqual(x.l, p.l)
        self.assertIs(x.l, p.l)

        unboxed(p, 'unassigned') << 1
        self.assertEqual(1, unboxed(p).unassigned)
        self.assertFalse(hasattr(x, 'unassigned'))
