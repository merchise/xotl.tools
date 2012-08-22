#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.memoize
#----------------------------------------------------------------------
# Copyright (c) 2011 Merchise Autrement
# All rights reserved.
#
# Author: Manuel Vázquez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Dec 21, 2011


'''
Provides a simple_memoize decorator to cache functions results.

.. autoclass:: simple_memoize
   :members:

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

from xoutil.deprecation import deprecated
from xoutil.functools import lru_cache, wraps

__docstring_format__ = 'rst'
__author__ = 'manu'



class _sizeable(type):
    'Simple metaclass to make simple_memoize have a __len__ method.'
    def __len__(self):
        return len(self.cache)


@deprecated(lru_cache)
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

    The second time the result will be retrieved from cache and won't be
    printed::

        >>> identity(1)
        1

    .. warning:: Use this only for small (or fixed) time-running applications.
                 Since it may increase the memory consumption considerably.

                 In a future release we will provide a fixed-sized (LRU-based)
                 cache by back-porting `functools.lru_cache` from Python 3.2.

    *Deprecated* since 1.1.0 in favor of :func:`xoutil.functools.lru_cache`.
    '''

    __metaclass__ = _sizeable

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
        '''
        Invalidates the cache for the function `func` with arguments
        `args`.

        ::

            >>> @simple_memoize
            ... def fib(n):
            ...    if n <= 1:
            ...        return 1
            ...    else:
            ...        return fib(n-2) + fib(n-1)

        Given this memoized function you may execute::

            >>> fib(50)
            20365011074

        Now the size of the ``simple_memoize``'s cache is::

            >>> len(simple_memoize)
            52

        If you invalidate some of numbers lesser than 50::

            >>> simple_memoize.invalidate(fib, (10, ))
            >>> len(simple_memoize)
            51

        '''
        from xoutil.objects import smart_getattr
        func = smart_getattr('simple_memoize_orig_func', func) or func
        if (func, args) in cls.cache:
            del cls.cache[(func, args)]
