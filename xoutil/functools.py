#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.functools
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
# Created on Feb 22, 2012

'''
Extensions to the `functools` module from the Python's standard library.

You may use this module as drop-in replacement of `functools`.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)


from functools import *
from xoutil.compat import py32


if not py32:
    from threading import Lock
    from xoutil.collections import _CacheInfo, OrderedDict

    # Back-ported lru_cache from py32. But take note that if running with at
    # least py32 we will use Python's version, so don't mess with internals.
    def lru_cache(maxsize=100):
        """Least-recently-used cache decorator.

        If *maxsize* is set to None, the LRU features are disabled and the
        cache can grow without bound.

        Arguments to the cached function must be hashable.

        View the cache statistics named tuple (hits, misses, maxsize,
        currsize) with f.cache_info().  Clear the cache and statistics with
        f.cache_clear(). Access the underlying function with f.__wrapped__.

        See:  http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used

        """
        # Users should only access the lru_cache through its public API:
        #       cache_info, cache_clear, and f.__wrapped__
        # The internals of the lru_cache are encapsulated for thread safety and
        # to allow the implementation to change (including a possible C version).

        def decorating_function(user_function,
                    tuple=tuple, sorted=sorted, len=len, KeyError=KeyError):

            _cache_info = [0, 0]
            kwd_mark = (object(),)          # separates positional and keyword args
            lock = Lock()                   # needed because OrderedDict isn't threadsafe

            if maxsize is None:
                cache = dict()              # simple cache without ordering or size limit

                @wraps(user_function)
                def wrapper(*args, **kwds):
                    #~ nonlocal hits, misses
                    hits, misses = _cache_info
                    key = args
                    if kwds:
                        key += kwd_mark + tuple(sorted(kwds.items()))
                    try:
                        result = cache[key]
                        hits += 1
                        _cache_info[0] = hits
                        _cache_info[1] = misses
                        return result
                    except KeyError:
                        pass
                    result = user_function(*args, **kwds)
                    cache[key] = result
                    misses += 1
                    _cache_info[0] = hits
                    _cache_info[1] = misses
                    return result
            else:
                cache = OrderedDict()           # ordered least recent to most recent
                cache_popitem = cache.popitem
                cache_renew = cache.move_to_end

                @wraps(user_function)
                def wrapper(*args, **kwds):
                    #~ nonlocal hits, misses
                    hits, misses = _cache_info
                    key = args
                    if kwds:
                        key += kwd_mark + tuple(sorted(kwds.items()))
                    with lock:
                        try:
                            result = cache[key]
                            cache_renew(key)    # record recent use of this key
                            hits += 1
                            _cache_info[0] = hits
                            _cache_info[1] = misses
                            return result
                        except KeyError:
                            pass
                    result = user_function(*args, **kwds)
                    with lock:
                        cache[key] = result     # record recent use of this key
                        misses += 1
                        if len(cache) > maxsize:
                            cache_popitem(0)    # purge least recently used cache entry
                    _cache_info[0] = hits
                    _cache_info[1] = misses
                    return result

            def cache_info():
                """Report cache statistics"""
                with lock:
                    return _CacheInfo(_cache_info[0], _cache_info[1], maxsize, len(cache))

            def cache_clear():
                """Clear the cache and cache statistics"""
                #~ nonlocal hits, misses
                with lock:
                    cache.clear()
                    _cache_info[0] = _cache_info[1] = 0

            wrapper.cache_info = cache_info
            wrapper.cache_clear = cache_clear
            return wrapper

        return decorating_function
