#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xotl.util.memoize
#----------------------------------------------------------------------
# Copyright (c) 2011 Merchise Autrement
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
# Created on Dec 21, 2011

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

__docstring_format__ = 'rst'
__author__ = 'manu'


from functools import wraps

class simple_memoize(object):
    '''
    A simple memoization decorator. It simply caches the result of pure
    functions (that does not depend on anything else than its own arguments)::

        >>> @simple_memoize
        ... def identity(value):
        ...    print 'Mirror:', value
        ...    return value

        >>> identity(1)
        Mirror: 1
        1

        # The second time the result will be retrieved from cache and won't be printed
        >>> identity(1)
        1

    Warning: Use this only for small (or fixed) time-running applications. Since
    it may increase the memory consumption considerably.'''
    cache = {}

    def __new__(cls, func):
        if getattr(func, 'simple_memoize_orig_func', None) is None:
            @wraps(func)
            def inner(*args):
                cache = cls.cache
                if (func, args) not in cache:
                    cache[(func, args)] = func(*args)
                return cache[(func, args)]
            inner.simple_memoize_orig_func = func
        else:
            return func
        return inner

    @classmethod
    def invalidate(cls, func, args):
        from xotl import smart_getattr
        func = smart_getattr('simple_memoize_orig_func', func) or func
        if (func, args) in cls.cache:
            del cls.cache[(func, args)]
