# Copied from Python 3.3 base code
#
# Copyright (c) 2001-2012, 2017 Python Software Foundation.  All rights reserved.
#

from xotl.tools.future import functools
import unittest
from random import choice


class TestLRU(unittest.TestCase):
    def test_lru(self):
        def orig(x, y):
            return 3 * x + y

        f = functools.lru_cache(maxsize=20)(orig)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(maxsize, 20)
        self.assertEqual(currsize, 0)
        self.assertEqual(hits, 0)
        self.assertEqual(misses, 0)

        domain = range(5)
        for i in range(1000):
            x, y = choice(domain), choice(domain)
            actual = f(x, y)
            expected = orig(x, y)
            self.assertEqual(actual, expected)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertTrue(hits > misses)
        self.assertEqual(hits + misses, 1000)
        self.assertEqual(currsize, 20)

        f.cache_clear()  # test clearing
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 0)
        self.assertEqual(misses, 0)
        self.assertEqual(currsize, 0)
        f(x, y)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 0)
        self.assertEqual(misses, 1)
        self.assertEqual(currsize, 1)

        # Test bypassing the cache
        self.assertIs(f.__wrapped__, orig)
        f.__wrapped__(x, y)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 0)
        self.assertEqual(misses, 1)
        self.assertEqual(currsize, 1)

        # test size zero (which means "never-cache")
        @functools.lru_cache(0)
        def f():
            global f_cnt
            f_cnt += 1
            return 20

        self.assertEqual(f.cache_info().maxsize, 0)
        global f_cnt
        f_cnt = 0
        for i in range(5):
            self.assertEqual(f(), 20)
        self.assertEqual(f_cnt, 5)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 0)
        self.assertEqual(misses, 5)
        self.assertEqual(currsize, 0)

        # test size one
        @functools.lru_cache(1)
        def f():
            global f_cnt
            f_cnt += 1
            return 20

        self.assertEqual(f.cache_info().maxsize, 1)
        f_cnt = 0
        for i in range(5):
            self.assertEqual(f(), 20)
        self.assertEqual(f_cnt, 1)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 4)
        self.assertEqual(misses, 1)
        self.assertEqual(currsize, 1)

        # test size two
        @functools.lru_cache(2)
        def f(x):
            global f_cnt
            f_cnt += 1
            return x * 10

        self.assertEqual(f.cache_info().maxsize, 2)
        f_cnt = 0
        for x in 7, 9, 7, 9, 7, 9, 8, 8, 8, 9, 9, 9, 8, 8, 8, 7:
            #    *  *              *                          *
            self.assertEqual(f(x), x * 10)
        self.assertEqual(f_cnt, 4)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 12)
        self.assertEqual(misses, 4)
        self.assertEqual(currsize, 2)

    def test_lru_with_maxsize_none(self):
        @functools.lru_cache(maxsize=None)
        def fib(n):
            if n < 2:
                return n
            return fib(n - 1) + fib(n - 2)

        self.assertEqual(
            [fib(n) for n in range(16)],
            [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610],
        )
        self.assertEqual(
            fib.cache_info(),
            functools._CacheInfo(hits=28, misses=16, maxsize=None, currsize=16),
        )
        fib.cache_clear()
        self.assertEqual(
            fib.cache_info(),
            functools._CacheInfo(hits=0, misses=0, maxsize=None, currsize=0),
        )

    def test_lru_with_exceptions(self):
        # Verify that user_function exceptions get passed through without
        # creating a hard-to-read chained exception.
        # http://bugs.python.org/issue13177
        for maxsize in (None, 100):

            @functools.lru_cache(maxsize)
            def func(i):
                return "abc"[i]

            self.assertEqual(func(0), "a")
            with self.assertRaises(IndexError) as cm:  # noqa
                func(15)
            #  The following is only valid in Py33 PEP 3143
            ##  self.assertIsNone(cm.exception.__context__)

            # Verify that the previous exception did not result in a cached
            # entry
            with self.assertRaises(IndexError):
                func(15)

    def test_lru_with_types(self):
        for maxsize in (None, 100):

            @functools.lru_cache(maxsize=maxsize, typed=True)
            def square(x):
                return x * x

            self.assertEqual(square(3), 9)
            self.assertEqual(type(square(3)), type(9))
            self.assertEqual(square(3.0), 9.0)
            self.assertEqual(type(square(3.0)), type(9.0))
            self.assertEqual(square(x=3), 9)
            self.assertEqual(type(square(x=3)), type(9))
            self.assertEqual(square(x=3.0), 9.0)
            self.assertEqual(type(square(x=3.0)), type(9.0))
            self.assertEqual(square.cache_info().hits, 4)
            self.assertEqual(square.cache_info().misses, 4)
