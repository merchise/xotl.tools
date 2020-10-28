#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import unittest
from xotl.tools.bound import boundary, whenall, whenany


def fibonacci(wait=None):
    import time

    a, b = 1, 1
    while True:
        if wait:
            time.sleep(wait)
        yield a
        a, b = b, a + b


class TestBoundedWithStandardPredicates(unittest.TestCase):
    def test_times(self):
        from xotl.tools.bound import times, until

        fib8 = times(8)(fibonacci)
        # Fibonacci numbers are yielded:
        # 1 1 2 3 5 8 13 21
        self.assertEqual(fib8(), 21)

        fib8 = until(times=8)(fibonacci)
        # Fibonacci numbers are yielded:
        # 1 1 2 3 5 8 13 21
        self.assertEqual(fib8(), 21)

        fib8 = times(8)(fibonacci)

        fib8gen = fib8.generate()  # exposed bounded generator
        self.assertEqual(tuple(fib8gen), (1, 1, 2, 3, 5, 8, 13, 21))

    def test_until_error(self):
        from xotl.tools.bound import until

        d = dict(a=1, b=2, c=3, d=4)

        @until(errors=(KeyError,))
        def getall(d, *keys):
            for k in keys:
                yield d[k]

        assert d["d"] == getall(d, "a", "b", "d")
        assert d["a"] == getall(d, "a", "kkk")

        @until(errors=(ValueError,))
        def getall(d, *keys):
            for k in keys:
                yield d[k]

        with self.assertRaises(KeyError):
            getall(d, "kkk")

        @until(errors=(RuntimeError,))
        def failing():
            raise RuntimeError
            yield 1

        assert failing() is None
        assert list(failing.generate()) == []

    def test_timed(self):
        from xotl.tools.bound import timed, until

        fib10ms = timed(1 / 100)(fibonacci)
        # Since the wait time below will be larger than the allowed execution
        # (10 ms) fib1ms will only be able to yield a single value (notice
        # that `timed` always allow a cycle.)
        res = fib10ms(wait=1 / 10)
        self.assertEqual(res, 1)

        fib10ms = until(maxtime=1 / 100)(fibonacci)
        # Since the wait time below will be larger than the allowed execution
        # (10 ms) fib1ms will only be able to yield a single value (notice
        # that `timed` always allow a cycle.)
        res = fib10ms(wait=1 / 10)
        self.assertEqual(res, 1)

        # If the time boundary is too low timed will allow not allow a cycle.
        fib0ms = timed(0)(fibonacci)
        res = fib0ms()
        self.assertEqual(res, None)

    def test_accumulated(self):
        from xotl.tools.bound import until
        from xotl.tools.bound import accumulated, timed, times

        # 1 + 1 + 2 + 3 + 5 + 8 + 13 + 21 + 34 + 55 + 89 + 144 = 376
        # ^   ^        ...                                  ^
        # |   |        ...                                  |
        # 1   2   3   4   5   6    7    8    9   10   11    12    13
        # |   |        ...                                  |     |
        # V   V        ...                                  V     V
        # 1 + 1 + 2 + 3 + 5 + 8 + 13 + 21 + 34 + 55 + 89 + 144 + 233 = 609
        fib500 = accumulated(500)(fibonacci)
        self.assertEqual(fib500(), 233)
        fib500 = until(accumulate=500)(fibonacci)
        self.assertEqual(fib500(), 233)

        fib500timed = whenall(accumulated(500), timed(0))(fibonacci)
        self.assertEqual(fib500timed(), 233)

        self.assertEqual(
            tuple(fib500.generate()), (1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233)
        )

        # With .generate()  you may count
        self.assertEqual(len(tuple(fib500.generate())), 13)  # the 13th

        # Since 500 is reached at the 13th fib number, looping up to the 20th
        # number must be bigger.
        fib500at20 = whenall(accumulated(500), times(20))(fibonacci)
        self.assertGreater(fib500at20(), 233)


class TestBoundaryDefinitions(unittest.TestCase):
    def test_argless_boundary(self):
        @boundary
        def argless():
            yield False  # receive args
            yield False  # allow first yield
            yield True

        # the following simulates:
        #   @argless
        #   def fibonacci():
        #      ....
        fib2 = argless(fibonacci)
        self.assertEqual(fib2(), 1)


class TestHigherLevelPreds(unittest.TestCase):
    def test_close_is_always_called(self):
        @boundary
        def bailout():
            yield
            try:
                yield False
                yield True
            except GeneratorExit:
                pass
            else:
                raise AssertionError("close() must have been called")

        fibnone = whenall(whenany(bailout))(fibonacci)
        self.assertEqual(fibnone(), 1)

    def test_whenall_with_invalid(self):
        from xotl.tools.bound import times

        @boundary
        def invalid():
            yield

        fibinv = whenall(invalid, times(10))(fibonacci)
        with self.assertRaises(RuntimeError):
            fibinv()

    def test_whenall_with_invalid_befored_terminated(self):
        from xotl.tools.bound import times

        @boundary
        def invalid():
            yield
            yield False

        fibinv = whenall(invalid, times(10))(fibonacci)
        with self.assertRaises(RuntimeError):
            fibinv()


class TestBoundedUnnamedPredicates(unittest.TestCase):
    def test_atmost_unnamed(self):
        from xotl.tools.bound import times

        fib8 = times(8)(fibonacci)
        # Fibonacci numbers are yielded:
        # 1 1 2 3 5 8 13 21
        self.assertEqual(fib8(), 21)

    def test_invalid_unnamed(self):
        @boundary
        def invalid():
            return 1

        @invalid
        def foobar():
            while True:
                yield

        with self.assertRaises(TypeError):
            foobar()

        @boundary
        def invalid_init():
            yield

        @invalid_init
        def foobar2():
            while True:
                yield

        with self.assertRaises(RuntimeError):
            foobar2()


class TestBoundedPredicates(unittest.TestCase):
    def test_invalid_predicate_early_at_init(self):
        @boundary
        def invalid():
            yield

        @invalid
        def foobar():
            pass

        with self.assertRaises(RuntimeError):
            foobar()

    def test_invalid_predicate_early_at_cycle(self):
        @boundary
        def invalid():
            yield
            yield False  # i.e never signal True

        @invalid
        def foobar():
            passes, atmost = 0, 10
            while passes < atmost:
                yield passes
                passes += 1
            raise AssertionError("Invalid reach point a GeneratorExit was expected.")

        with self.assertRaises(RuntimeError):
            foobar()


class TestMisc(unittest.TestCase):
    def test_args_are_passed(self):
        @boundary
        def pred():
            args, kwargs = yield
            self.assertEqual(args, (1, 2))
            self.assertEqual(kwargs, {})
            yield True

        @pred
        def foobar(*args, **kwargs):
            while True:
                yield 1

        foobar(1, 2)

    def test_whens_receives_args(self):
        from xotl.tools.bound import whenall, whenany

        self.assertTrue(whenall.receive_args)
        self.assertTrue(whenany.receive_args)

    def test_args_are_passed_to_all(self):
        from xotl.tools.bound import whenall, whenany

        @boundary
        def pred():
            args, kwargs = yield
            self.assertEqual(args, (1, 2))
            self.assertEqual(kwargs, {"egg": "ham"})
            yield True

        @whenall(pred, pred())
        def foobar(*args, **kwargs):
            while True:
                yield 1

        foobar(1, 2, egg="ham")

        @whenany(pred(), pred)
        def foobar(*args, **kwargs):
            while True:
                yield 1

        foobar(1, 2, egg="ham")

    def test_needs_args(self):
        from xotl.tools.bound import times

        @whenall(times)
        def foobar():
            yield

        with self.assertRaises(TypeError):
            foobar()  # times is not initialized

    def test_plain_function(self):
        def pred():
            args, kwargs = yield
            self.assertEqual(args, (1, 2))
            self.assertEqual(kwargs, {"egg": "ham"})
            yield True

        @whenall(pred)
        def foobar(*args, **kwargs):
            while True:
                yield 1

        foobar(1, 2, egg="ham")

    def test_generators(self):
        def pred():
            args, kwargs = yield
            self.assertEqual(args, (1, 2))
            self.assertEqual(kwargs, {"egg": "ham"})
            yield True

        @whenall(pred())  # a generator!!
        def foobar(*args, **kwargs):
            while True:
                yield 1

        foobar(1, 2, egg="ham")

    def test_plain_generator(self):
        from xotl.tools.bound import times

        fibseq = fibonacci()
        limited = times(5)(fibseq)
        self.assertEqual(limited(), 5)


class TestTerminationCases(unittest.TestCase):
    def test_termination_when_exception(self):
        def magic_number(a):
            if a < 1:
                yield 0
            else:
                prev = next(magic_number(a - 1))
                yield a + prev

        @boundary
        def forever():
            try:
                while True:
                    yield False
            except GeneratorExit:
                pass  # ok
            else:
                raise AssertionError("close() not called to boundary")

        bounded = forever()(magic_number)
        bounded(0)  # No exception
        with self.assertRaises(TypeError):
            bounded("invalid")
