#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_functools
#----------------------------------------------------------------------
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
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)

from contextlib import contextmanager
from datetime import datetime, timedelta

from xoutil.functools import lru_cache

__docstring_format__ = 'rst'
__author__ = 'manu'


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
    with takes_no_more_than(90):
        assert fib(120) == 8670007398507948658051921
