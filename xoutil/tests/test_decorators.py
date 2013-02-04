#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_decorators
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# Copyright (c) 2011, 2012 Medardo Rodríguez
# All rights reserved.
#
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Nov 18, 2011

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

__docstring_format__ = 'rst'
__author__ = 'manu'

import unittest
from xoutil.decorator import assignment_operator
from xoutil.decorator.meta import decorator


class TestAssignable(unittest.TestCase):
    def test_inline_expression(self):
        @assignment_operator()
        def test(name, *args):
            return name * (len(args) + 1)

        self.assertEqual('aaa', test('a', 1, 2))

    def test_assignment(self):
        @assignment_operator()
        def test(name, *args):
            return name * (len(args) + 1)

        b = test(1, 2, 4)
        self.assertEqual('bbbb', b)

    def test_regression_inline(self):
        @assignment_operator(maybe_inline=True)
        def test(name, *args):
            if name:
                return name * (len(args) + 1)
            else:
                return None

        self.assertIs(None, test('a', 1, 2))

    def test_regression_on_block(self):
        @assignment_operator(maybe_inline=True)
        def union(name, *args):
            return (name,) + args

        for which in (union(1, 2),):
            self.assertEqual((None, 1, 2), which)


    def test_argsless_decorator(self):
        @decorator
        def log(func, fmt='Calling function %s'):
            def inner(*args, **kwargs):
                print(fmt % func.__name__)
                return func(*args, **kwargs)
            return inner

        @log
        def hello(msg='Hi'):
            print(msg)

        @log()
        def hi(msg='Hello'):
            print(msg)

        hi()
        hello()
        pass

    def test_returning_argless(self):
        @decorator
        def plus2(func, value=1):
            def inner(*args):
                return func(*args) + value
            return inner

        @plus2
        def ident2(val):
            return val

        @plus2()
        def ident3(val):
            return val

        self.assertEquals(ident2(10), 11)
        self.assertEquals(ident3(10), 11)


class RegressionTests(unittest.TestCase):
    def test_with_kwargs(self):
        'When passing a function as first positional argument, kwargs should be tested empty'
        from xoutil.functools import partial
        @decorator
        def ditmoi(target, *args, **kwargs):
            return partial(target, *args, **kwargs)

        def badguy(n):
            return n

        @ditmoi(badguy, b=1)
        def foobar(n, *args, **kw):
            return n

        self.assertEqual(badguy, foobar(1))


class TestMetaclassDecorator(unittest.TestCase):
    def setUp(self):
        from xoutil.decorator.compat import metaclass

        class FooMeta(type):
            def __new__(cls, name, bases, attrs):
                result = super(FooMeta, cls).__new__(cls, name, bases, attrs)
                result.foo_class = True
                return result

        class FooBarMeta(FooMeta):
            def __new__(cls, name, bases, attrs):
                result = super(FooBarMeta, cls).__new__(cls, name, bases, attrs)
                result.foobar_args = (name, bases)
                return result

        @metaclass(FooMeta)
        class FooClass(object):
            @staticmethod
            def static(*args):
                return args

            @classmethod
            def clsmethod(cls, *args):
                return (cls.foo_class, getattr(cls, 'foobar_args', ()))

            def get_or_set(self, name, value):
                from xoutil.objects import setdefaultattr
                result = setdefaultattr(self, name, value)
                return result


        @metaclass(FooBarMeta)
        class FooBarClass(FooClass):
            value = {1:2}

        self.FooClass = FooClass
        self.FooBarClass = FooBarClass


    def test_metaclass(self):
        from xoutil.types import is_classmethod, is_staticmethod, is_instancemethod
        FooClass = self.FooClass
        FooBarClass = self.FooBarClass

        self.assertTrue(FooClass.foo_class and FooBarClass.foo_class)
        self.assertEquals(('FooBarClass', (FooClass, )), FooBarClass.foobar_args)

        self.assertTrue(is_classmethod(FooClass, 'clsmethod'))
        self.assertTrue(is_staticmethod(FooClass, 'static'))
        self.assertTrue(is_instancemethod(FooClass, 'get_or_set'))

        self.assertTrue(is_classmethod(FooBarClass, 'clsmethod'))
        self.assertTrue(is_staticmethod(FooBarClass, 'static'))
        self.assertTrue(is_instancemethod(FooBarClass, 'get_or_set'))


if __name__ == "__main__":
    unittest.main(verbosity=2)
