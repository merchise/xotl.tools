#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import unittest

from xotl.tools.decorator.meta import decorator


class TestAssignable(unittest.TestCase):
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
        from functools import partial

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
        self.assertNotEqual(getattr_static(foo, "prop"), foo)
        self.assertIs(foo.prop, foo)
        self.assertIs(getattr_static(foo, "prop"), foo)
        # After the first invocation, the static attr is the result.
        Foobar.prop.reset(foo)
        self.assertNotEqual(getattr_static(foo, "prop"), foo)


if __name__ == "__main__":
    unittest.main(verbosity=2)
