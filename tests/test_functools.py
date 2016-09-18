#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_functools
#----------------------------------------------------------------------
# Copyright (c) 2015, 2016 Merchise and Contributors
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
# Created on Jul 3, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        # unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)

import unittest

from contextlib import contextmanager
from datetime import datetime, timedelta

from xoutil.future.functools import lru_cache


@lru_cache(3)
def fib(n):
    print(n)
    if n <= 1:
        return 1
    else:
        # It seems that there's a difference in the execution path for `return
        # fib(n-2) + fib(n-1)` between Python 2.7 and Python 3.2, so let's make
        # more explicit the order we'd like so the test is more reliable.
        a = fib(n-1)
        b = fib(n-2)
        return a + b


def takes_no_more_than(duration, msg=None):
    if not msg:
        msg = 'It took longer than {s} seconds'.format(s=duration)

    @contextmanager
    def inner():
        start = datetime.now()
        yield
        end = datetime.now()
        max_duration = timedelta(seconds=duration)
        if (end - start) > max_duration:
            raise AssertionError(msg)
    return inner()


def test_lrucache():
    # Without caching fib(120) would take ages.  On a 2.20GHz laptop with
    # caching this takes less than 1 sec, so let's test that it will respond in
    # no more than 3 min to allow very slow machines testing this code.
    fib.cache_clear()
    with takes_no_more_than(90):
        assert fib(120) == 8670007398507948658051921


def test_lrucache_stats():
    pass


from xoutil.future.functools import compose


class TestCompose(unittest.TestCase):
    def test_needs_at_least_an_argument(self):
        with self.assertRaises(TypeError):
            compose()

    def test_single_argument_is_identitical(self):
        def anything():
            pass

        self.assertIs(anything, compose(anything))

    def test_only_callables(self):
        with self.assertRaises(TypeError):
            compose(1)

    def test_simple_case(self):
        incr = lambda x: x + 1
        add_3 = compose(incr, incr, incr)
        self.assertEqual(3, add_3(0))

    def test_with_pow(self):
        from xoutil.future.functools import power
        incr = lambda x: x + 1
        add_1 = power(incr, 1)
        self.assertIs(incr, add_1)
        add_3 = power(incr, 3)
        self.assertEqual(3, add_3(0))

    def test_ctuple(self):
        from xoutil.eight import range
        from xoutil.future.functools import ctuple

        def echo(*args):
            return args

        result = compose(echo, ctuple, list, range, math=False)(10)
        expected = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        self.assertEqual(expected, result)

        # Without ctuple prints the list
        result = compose(echo, list, range, math=False)(10)
        expected = ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], )
        self.assertEqual(expected, result)

def test_lwraps():
    from xoutil.future.functools import lwraps

    class foobar(object):
        @lwraps('method-one', one=True)
        def one(self):
            return type(self).__name__

        @lwraps('method-two', two=True)
        @classmethod
        def two(cls):
            return cls.__name__

        @lwraps('method-three', three=True)
        @staticmethod
        def three():
            return 'foobar'

    @lwraps('function-four', four=True, one=False)
    def four(*args):
        return [(arg.__name__, arg()) for arg in args]

    f = foobar()
    names = ('method-one', 'method-two', 'method-three', 'function-four')

    assert four.__name__ == names[3]
    assert foobar.one.__name__ == names[0]
    assert foobar.two.__name__ == names[1]
    assert foobar.three.__name__ == names[2]
    assert f.one.__name__ == names[0]
    assert f.two.__name__ == names[1]
    assert f.three.__name__ == names[2]

    assert four.four
    assert not four.one
    assert f.one.one
    assert f.two.two
    assert f.three.three

    for i, (a, b) in enumerate(four(f.one, f.two, f.three)):
        assert a == names[i]
        assert b == 'foobar'
