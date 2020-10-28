#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import unittest
from xotl.tools.decorator import assignment_operator
from xotl.tools.decorator.meta import decorator


class TestAssignable(unittest.TestCase):
    def test_inline_expression(self):
        @assignment_operator()
        def test(name, *args):
            return name * (len(args) + 1)

        self.assertEqual("aaa", test("a", 1, 2))

    def test_assignment(self):
        @assignment_operator()
        def test(name, *args):
            return name * (len(args) + 1)

        b = test(1, 2, 4)
        self.assertEqual("bbbb", b)

    def test_regression_inline(self):
        @assignment_operator(maybe_inline=True)
        def test(name, *args):
            if name:
                return name * (len(args) + 1)
            else:
                return None

        self.assertIs(None, test("a", 1, 2))

    def test_regression_on_block(self):
        @assignment_operator(maybe_inline=True)
        def union(name, *args):
            return (name,) + args

        for which in (union(1, 2),):
            self.assertEqual((None, 1, 2), which)

    def test_argsless_decorator(self):
        @decorator
        def log(func, fmt="Calling function %s"):
            def inner(*args, **kwargs):
                print(fmt % func.__name__)
                return func(*args, **kwargs)

            return inner

        @log
        def hello(msg="Hi"):
            print(msg)

        @log()
        def hi(msg="Hello"):
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

        self.assertEqual(ident2(10), 11)
        self.assertEqual(ident3(10), 11)


class RegressionTests(unittest.TestCase):
    def test_with_kwargs(self):
        """When passing a function as first positional argument, kwargs should
        be tested empty.

        """
        from xotl.tools.future.functools import partial

        @decorator
        def ditmoi(target, *args, **kwargs):
            return partial(target, *args, **kwargs)

        def badguy(n):
            return n

        @ditmoi(badguy, b=1)
        def foobar(n, *args, **kw):
            return n

        self.assertEqual(badguy, foobar(1))


class Memoizations(unittest.TestCase):
    def test_memoized_property(self):
        from xotl.tools.future.inspect import getattr_static
        from xotl.tools.objects import memoized_property

        class Foobar:
            @memoized_property
            def prop(self):
                return self

            with self.assertRaises(AttributeError):

                @prop.setter
                def prop(self, value):
                    pass

            with self.assertRaises(AttributeError):

                @prop.deleter
                def prop(self, value):
                    pass

        foo = Foobar()
        self.assertNotEquals(getattr_static(foo, "prop"), foo)
        self.assertIs(foo.prop, foo)
        self.assertIs(getattr_static(foo, "prop"), foo)
        # After the first invocation, the static attr is the result.
        Foobar.prop.reset(foo)
        self.assertNotEquals(getattr_static(foo, "prop"), foo)


class ConstantBags(unittest.TestCase):
    def test_constant_bags_decorator(self):
        from xotl.tools.decorator import constant_bagger as typify

        def func(**kwds):
            return kwds

        bag = func(ONE=1, TWO=2)

        @typify(ONE=1, TWO=2)
        def BAG(**kwds):
            return kwds

        self.assertIs(type(BAG), type)
        self.assertIn("ONE", bag)
        self.assertEqual(bag["ONE"], BAG.ONE)
        self.assertEqual(BAG.TWO, 2 * BAG.ONE)
        with self.assertRaises(AttributeError):
            self.assertEqual(bag.TWO, 2 * bag.ONE)
        with self.assertRaises(TypeError):
            self.assertEqual(BAG["TWO"], 2 * BAG["ONE"])
        with self.assertRaises(AttributeError):
            self.assertEqual(BAG.THREE, 3)
        self.assertIs(BAG(THREE=3), BAG)
        self.assertEqual(BAG.THREE, 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
