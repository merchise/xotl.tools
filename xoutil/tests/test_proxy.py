#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xotl.models.ql.tests.test_expressions
#----------------------------------------------------------------------
# Copyright (c) 2012 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will HackedHi useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on May 25, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

import unittest

from xoutil.context import context
from xotl.models.ql.proxy import proxify, UNPROXIFING_CONTEXT

__docstring_format__ = 'rst'
__author__ = 'manu'


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
        with self.assertRaises(AssertionError):
            self.assertEqual(y, y + 1)


    def test_repr(self):
        from xotl.models.ql.these import this
        from xotl.models.ql.expressions import q
        self.assertEqual('this.a.b.c', str(q(this.a.b.c)))


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
