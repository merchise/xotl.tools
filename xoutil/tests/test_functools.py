#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_functools
#----------------------------------------------------------------------
# Copyright (c) 2012 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on Jul 3, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)

import unittest

from xoutil.functools import lru_cache

__docstring_format__ = 'rst'
__author__ = 'manu'



class TestFunctools(unittest.TestCase):
    def assertTakesNoMoreThan(self, seconds, msg=None):
        from contextlib import contextmanager
        from datetime import datetime, timedelta

        if not msg:
            msg = 'It took longer than {s} seconds'.format(s=seconds)

        @contextmanager
        def inner():
            start = datetime.now()
            yield
            end = datetime.now()
            max_duration = timedelta(seconds=seconds)
            if (end - start) > max_duration:
                raise self.failureException(msg)

        return inner()

    def test_lrucache(self):
        # For acceleration purposes only 2 is needed. Of course, you may
        # implement a non-recursive fib function easily, but that's not the
        # point here.
        @lru_cache(2)
        def fib(n):
            if n <= 1:
                return 1
            else:
                return fib(n-2) + fib(n-1)

        # Without caching fib(120) would take ages
        # On a 2.20GHz laptop this takes less than 1 sec, so let's test
        # that it will respond in no more than 3 min.
        with self.assertTakesNoMoreThan(90):
            self.assertEqual(8670007398507948658051921, fib(120))

        hits, misses, _max, currsize = fib.cache_info()
        self.assertEqual(0, hits)
        self.assertEqual(1, misses)
        self.assertEqual(2, currsize)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(verbosity=2)
