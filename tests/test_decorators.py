#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_decorators
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
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
        '''When passing a function as first positional argument, kwargs should be
        tested empty.

        '''
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

if __name__ == "__main__":
    unittest.main(verbosity=2)
