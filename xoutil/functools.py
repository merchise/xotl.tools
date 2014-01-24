#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.functools
#----------------------------------------------------------------------
#
# Most of the code of this file is backported from Python 3.2 standard library
# with minor modifications to make it work on Python 2.7. So, this file is
# distributed under the terms of the Python Software Foundatation Licence for
# Python 3.2.
#
# Created on Feb 22, 2012

'''Extensions to the `functools` module from the Python's standard library.

You may use this module as drop-in replacement of `functools`.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)


from xoutil.modules import copy_members as _copy_python_module_members
_pm = _copy_python_module_members()
wraps = _pm.wraps

from xoutil.names import strlist as strs
__all__ = strs('ctuple', 'compose', 'power', 'lru_cache')
del _pm, _copy_python_module_members, strs

from xoutil.compat import py32, callable
from xoutil.deprecation import deprecated


class ctuple(tuple):
    '''Simple tuple marker for :func:`compose`.

    Since is a callable you may use it directly in ``compose`` instead of
    changing your functions to returns ctuples instead of tuples::

       >>> def compat_print(*args):
       ...     for arg in args:
       ...         print arg,
       ...     print

       >>> compose(compat_print, ctuple, list, range, math=False)(10)
       0 1 2 3 4 5 6 7 8 9

       # Without ctuple prints the list
       >>> compose(compat_print, list, range, math=False)(10)
       [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    '''


def compose(*funcs, **kwargs):
    '''Returns a function that is the composition of `funcs`.

    By default `compose` behaves like mathematical function composition: this
    is to say that ``compose(f1, ... fn)`` is equivalent to ``lambda _x:
    fn(...(f1(_x))...)``.

    If any "intermediate" function returns a :class:`ctuple` is expanded as
    several positional arguments to the next function.

    :param math: Indicates if `compose` should behave like mathematical
                 function composition: last function in `funcs` is applied
                 last. If False, then the last function in `func` is applied
                 first.
    '''
    math = kwargs.get('math', True)
    if not math:
        funcs = list(reversed(funcs))
    def _inner(*args):
        f, functions = funcs[0], funcs[1:]
        result = f(*args)
        for f in functions:
            if isinstance(result, ctuple):
                result = f(*result)
            else:
                result = f(result)
        return result
    return _inner


# The real signature should be (*funcs, times)
def power(*args):
    '''Returns the "power" composition of several functions.

    Examples::

       >>> import operator
       >>> f = power(partial(operator.mul, 3), 3)
       >>> f(23) == 3*(3*(3*23))
       True

       >>> power(operator.neg)
       Traceback (most recent call last):
       ...
       TypeError: Function `power` requires at least two arguments
    '''
    try:
        funcs, times = args[:-1], args[-1]
    except IndexError:
        msg = "Function `power` requires at least two arguments"
        raise TypeError(msg)
    if not funcs:
        raise TypeError('Function `power` requires at least two arguments')
    if any(not callable(func) for func in funcs):
        raise TypeError('First arguments of `power` must be callables')
    if not isinstance(times, int):
        raise TypeError('Last argument of `power` must be int')
    if len(funcs) > 1:
        base = (compose(funcs), )
    else:
        base = (funcs[0], )
    return compose(*(base * times))


if not py32:
    from threading import Lock
    from xoutil.collections import _CacheInfo, OrderedDict

    # Back-ported lru_cache from py32. But take note that if running with at
    # least py32 we will use Python's version, so don't mess with internals.
    def lru_cache(maxsize=100):
        '''Least-recently-used cache decorator.

        If *maxsize* is set to None, the LRU features are disabled and the
        cache can grow without bound.

        Arguments to the cached function must be hashable.

        View the cache statistics named tuple (hits, misses, maxsize,
        currsize) with f.cache_info().  Clear the cache and statistics with
        f.cache_clear(). Access the underlying function with f.__wrapped__.

        See:  http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used

        '''
        # Users should only access the lru_cache through its public API:
        #       cache_info, cache_clear, and f.__wrapped__
        # The internals of the lru_cache are encapsulated for thread safety and
        # to allow the implementation to change (including a possible C
        # version).

        def decorating_function(user_function,
                    tuple=tuple, sorted=sorted, len=len, KeyError=KeyError):

            _cache_info = [0, 0]
            # separates positional and keyword args
            kwd_mark = (object(),)
            # needed because OrderedDict isn't threadsafe
            lock = Lock()

            if maxsize is None:
                # simple cache without ordering or size limit
                cache = {}

                @wraps(user_function)
                def wrapper(*args, **kwds):
                    #~ nonlocal hits, misses
                    hits, misses = tuple(_cache_info)
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
                cache = OrderedDict()     # ordered least recent to most recent
                cache_popitem = cache.popitem
                cache_renew = cache.move_to_end

                @wraps(user_function)
                def wrapper(*args, **kwds):
                    #~ nonlocal hits, misses
                    hits, misses = tuple(_cache_info)
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
                        _cache_info[0] = hits
                        _cache_info[1] = misses
                        if len(cache) > maxsize:
                            cache_popitem(0)    # purge least recently used
                    return result

            def cache_info():
                '''Report cache statistics'''
                with lock:
                    return _CacheInfo(_cache_info[0], _cache_info[1], maxsize,
                                      len(cache))

            def cache_clear():
                '''Clear the cache and cache statistics'''
                #~ nonlocal hits, misses
                with lock:
                    cache.clear()
                    _cache_info[0] = _cache_info[1] = 0

            wrapper.cache_info = cache_info
            wrapper.cache_clear = cache_clear
            return wrapper

        return decorating_function
