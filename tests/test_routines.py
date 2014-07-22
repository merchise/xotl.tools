# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# test_routines
#----------------------------------------------------------------------
# Copyright (c) 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-07-21


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


import unittest
from xoutil.decorator.routines import predicate, bounded


class TestRoutinesCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from xoutil.decorator.routines import _predicates
        cls._predicates = dict(_predicates)

    @classmethod
    def tearDownClass(cls):
        from xoutil.decorator.routines import _predicates
        _predicates.clear()
        _predicates.update(cls._predicates)

    def setUp(self):
        from xoutil.decorator.routines import _predicates
        _predicates.clear()
        _predicates.update(self._predicates)


def fibonacci(wait=None):
    import time
    a, b = 1, 1
    while True:
        if wait:
            time.sleep(wait)
        yield a
        a, b = b, a + b


class TestBoundedWithStandardPredicates(TestRoutinesCase):
    def test_assert_standard_predicates(self):
        from xoutil.decorator.routines import _predicates
        self.assertIn('timed', _predicates)
        self.assertIn('atmost', _predicates)
        self.assertIn('pred', _predicates)

    def test_atmost(self):
        fib8 = bounded(atmost=8)(fibonacci)
        # Fibonacci numbers are yielded:
        # 1 1 2 3 5 8 13 21
        self.assertEquals(fib8(), 21)

    def test_timed(self):
        fib10ms = bounded(timed=1/100)(fibonacci)
        # Since the wait time below will be larger than the allowed execution
        # (10 ms) fib1ms will only be able to yield a single value (notice
        # that `timed` always allow a cycle.)
        res = fib10ms(wait=1/10)
        self.assertEquals(res, 1)

        # If the time boundary is too low timed will allow a cycle
        fib0ms = bounded(timed=0)(fibonacci)
        res = fib0ms()
        self.assertEquals(res, 1)


class TestBoundedUnnamedPredicates(TestRoutinesCase):
    def test_atmost_unnamed(self):
        from xoutil.decorator.routines import atmost
        fib8 = bounded(atmost(8))(fibonacci)
        # Fibonacci numbers are yielded:
        # 1 1 2 3 5 8 13 21
        self.assertEquals(fib8(), 21)

    def test_invalid_unnamed(self):
        def invalid():
            return 1

        with self.assertRaises(TypeError):
            @bounded(invalid)
            def foobar():
                while True:
                    yield

        def invalid_init():
            yield

        @bounded(invalid_init)
        def foobar2():
            while True:
                yield

        with self.assertRaises(RuntimeError):
            foobar2()


class TestBoundedPredicates(TestRoutinesCase):
    def test_invalid_predicate_early_at_init(self):
        @predicate(name='invalid')
        def invalid(_):
            yield

        @bounded(invalid=1)
        def foobar():
            pass

        with self.assertRaises(RuntimeError):
            foobar()

    def test_invalid_predicate_early_at_cycle(self):
        @predicate(name='invalid')
        def invalid(_):
            yield
            yield False  # i.e never signal True

        @bounded(invalid=1)
        def foobar():
            passes, atmost = 0, 10
            while passes < atmost:
                yield passes
                passes += 1
            raise AssertionError('Invalid reach point a GeneratorExit was '
                                 'expected.')

        with self.assertRaises(RuntimeError):
            foobar()
