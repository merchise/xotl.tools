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
_pm_update_wrapper = _pm.update_wrapper
wraps, partial = _pm.wraps, _pm.partial
del _pm, _copy_python_module_members

import sys
py33 = sys.version_info >= (3, 3, 0)
del sys

from xoutil.six import callable


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


def compose(*callables, **kwargs):
    '''Returns a function that is the composition of several `callables`.

    By default `compose` behaves like mathematical function composition: this
    is to say that ``compose(f1, ... fn)`` is equivalent to ``lambda _x:
    fn(...(f1(_x))...)``.

    If any "intermediate" function returns a :class:`ctuple` it is expanded as
    several positional arguments to the next function.

    .. versionchanged:: 1.5.5 At least a callable must be passed, otherwise a
                        TypeError is raised.  If a single callable is passed
                        it is returned without change.

    :param math: Indicates if `compose` should behave like mathematical
                 function composition: last function in `funcs` is applied
                 last. If False, then the last function in `func` is applied
                 first.

    '''
    from xoutil.six import callable
    if not callables:
        raise TypeError('At least a function must be provided')
    if not all(callable(func) for func in callables):
        raise TypeError('Every func must a callable')
    if len(callables) == 1:
        return callables[0]
    math = kwargs.get('math', True)
    if not math:
        callables = list(reversed(callables))

    def _inner(*args):
        f, functions = callables[0], callables[1:]
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


if not py33:
    from threading import RLock
    from xoutil.collections import namedtuple

    _CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize",
                                          "currsize"])

    # Back-ported lru_cache from py33. But take note that if running with at
    # least py3 we will use Python's version, so don't mess with internals.

    WRAPPER_ASSIGNMENTS = ('__module__', '__name__', '__qualname__', '__doc__',
                           '__annotations__')
    WRAPPER_UPDATES = ('__dict__',)

    def update_wrapper(wrapper,
                       wrapped,
                       assigned=WRAPPER_ASSIGNMENTS,
                       updated=WRAPPER_UPDATES):
        """Update a wrapper function to look like the wrapped function

           wrapper is the function to be updated
           wrapped is the original function
           assigned is a tuple naming the attributes assigned directly
           from the wrapped function to the wrapper function (defaults to
           functools.WRAPPER_ASSIGNMENTS)
           updated is a tuple naming the attributes of the wrapper that
           are updated with the corresponding attribute from the wrapped
           function (defaults to functools.WRAPPER_UPDATES)
        """
        wrapper.__wrapped__ = wrapped
        for attr in assigned:
            try:
                value = getattr(wrapped, attr)
            except AttributeError:
                pass
            else:
                setattr(wrapper, attr, value)
        for attr in updated:
            getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
        # Return the wrapper so this can be used as a decorator via partial()
        return wrapper

    def wraps(wrapped,
              assigned=WRAPPER_ASSIGNMENTS,
              updated=WRAPPER_UPDATES):
        """Decorator factory to apply update_wrapper() to a wrapper function

           Returns a decorator that invokes update_wrapper() with the decorated
           function as the wrapper argument and the arguments to wraps() as the
           remaining arguments. Default arguments are as for update_wrapper().
           This is a convenience function to simplify applying partial() to
           update_wrapper().
        """
        return partial(update_wrapper, wrapped=wrapped,
                       assigned=assigned, updated=updated)

    class _HashedSeq(list):
        """ This class guarantees that hash() will be called no more than once
            per element.  This is important because the lru_cache() will hash
            the key multiple times on a cache miss.

        """

        __slots__ = 'hashvalue'

        def __init__(self, tup, hash=hash):
            self[:] = tup
            self.hashvalue = hash(tup)

        def __hash__(self):
            return self.hashvalue


    def _make_key(args, kwds, typed,
                  kwd_mark=(object(),),
                  fasttypes={int, str, frozenset, type(None)},
                  sorted=sorted, tuple=tuple, type=type, len=len):
        """Make a cache key from optionally typed positional and keyword
        arguments.

        The key is constructed in a way that is flat as possible rather than
        as a nested structure that would take more memory.

        If there is only a single argument and its data type is known to cache
        its hash value, then that argument is returned without a wrapper.
        This saves space and improves lookup speed.

        """
        key = args
        if kwds:
            sorted_items = sorted(kwds.items())
            key += kwd_mark
            for item in sorted_items:
                key += item
        if typed:
            key += tuple(type(v) for v in args)
            if kwds:
                key += tuple(type(v) for k, v in sorted_items)
        elif len(key) == 1 and type(key[0]) in fasttypes:
            return key[0]
        return _HashedSeq(key)

    def lru_cache(maxsize=128, typed=False):
        """Decorator to wrap a function with a memoizing callable that saves
        up to the `maxsize` most recent calls.  It can save time when an
        expensive or I/O bound function is periodically called with the same
        arguments.

        Since a dictionary is used to cache results, the positional and
        keyword arguments to the function must be hashable.

        If `maxsize` is set to None, the LRU feature is disabled and the cache
        can grow without bound.  The LRU feature performs best when maxsize is
        a power-of-two.

        If `typed` is set to True, function arguments of different types will
        be cached separately.  For example, ``f(3)`` and ``f(3.0)`` will be
        treated as distinct calls with distinct results.

        To help measure the effectiveness of the cache and tune the `maxsize`
        parameter, the wrapped function is instrumented with a cache_info()
        function that returns a named tuple showing hits, misses, maxsize and
        currsize.  In a multi-threaded environment, the hits and misses are
        approximate.

        The decorator also provides a ``cache_clear()`` function for clearing
        or invalidating the cache.

        The original underlying function is accessible through the
        ``__wrapped__`` attribute.  This is useful for introspection, for
        bypassing the cache, or for rewrapping the function with a different
        cache.

        An `LRU (least recently used)`__ cache works best when the most recent
        calls are the best predictors of upcoming calls (for example, the most
        popular articles on a news server tend to change each day).  The
        cache's size limit assures that the cache does not grow without bound
        on long-running processes such as web servers.

        __ http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used

        """

        # Users should only access the lru_cache through its public API:
        #       cache_info, cache_clear, and f.__wrapped__

        # The internals of the lru_cache are encapsulated for thread safety
        # and to allow the implementation to change (including a possible C
        # version).

        # Constants shared by all lru cache instances:
        sentinel = object()          # unique object used to signal cache misses
        make_key = _make_key         # build a key from the function arguments
        PREV, NEXT, KEY, RESULT = 0, 1, 2, 3   # names for the link fields

        def decorating_function(user_function):
            cache = {}
            hits = misses = 0
            _cache_vars = [hits, misses]  # hits, misses
            _HITS, _MISSES = 0, 1
            full = False
            # bound method to lookup a key or return None
            cache_get = cache.get
            # because linkedlist updates aren't threadsafe
            lock = RLock()
            # root of the circular doubly linked list
            root = []
            # initialize by pointing to self
            root[:] = [root, root, None, None]
            _cache_vars.extend([full, root])
            _FULL = 2
            _ROOT = 3

            if maxsize == 0:

                def wrapper(*args, **kwds):
                    # No caching -- just a statistics update after a
                    # successful call
                    # nonlocal misses
                    result = user_function(*args, **kwds)
                    _cache_vars[_MISSES] += 1
                    return result

            elif maxsize is None:

                def wrapper(*args, **kwds):
                    # Simple caching without ordering or size limit
                    #nonlocal hits, misses
                    key = make_key(args, kwds, typed)
                    result = cache_get(key, sentinel)
                    if result is not sentinel:
                        _cache_vars[_HITS] += 1
                        return result
                    result = user_function(*args, **kwds)
                    cache[key] = result
                    _cache_vars[_MISSES] += 1
                    return result

            else:

                def wrapper(*args, **kwds):
                    # Size limited caching that tracks accesses by recency
                    #nonlocal root, hits, misses, full
                    root = _cache_vars[_ROOT]
                    key = make_key(args, kwds, typed)
                    with lock:
                        link = cache_get(key)
                        if link is not None:
                            # Move the link to the front of the circular queue
                            link_prev, link_next, _key, result = link
                            link_prev[NEXT] = link_next
                            link_next[PREV] = link_prev
                            last = root[PREV]
                            last[NEXT] = root[PREV] = link
                            link[PREV] = last
                            link[NEXT] = root
                            _cache_vars[_HITS] += 1
                            return result
                    result = user_function(*args, **kwds)
                    with lock:
                        if key in cache:
                            # Getting here means that this same key was added
                            # to the cache while the lock was released.  Since
                            # the link update is already done, we need only
                            # return the computed result and update the count
                            # of misses.
                            pass
                        elif _cache_vars[_FULL]:
                            # Use the old root to store the new key and result.
                            oldroot = root = _cache_vars[_ROOT]
                            oldroot[KEY] = key
                            oldroot[RESULT] = result
                            # Empty the oldest link and make it the new root.
                            # Keep a reference to the old key and old result
                            # to prevent their ref counts from going to zero
                            # during the update. That will prevent potentially
                            # arbitrary object clean-up code (i.e. __del__)
                            # from running while we're still adjusting the
                            # links.
                            root = _cache_vars[_ROOT] = oldroot[NEXT]
                            oldkey = root[KEY]
                            oldresult = root[RESULT]
                            root[KEY] = root[RESULT] = None
                            # Now update the cache dictionary.
                            del cache[oldkey]
                            # Save the potentially reentrant cache[key]
                            # assignment for last, after the root and links
                            # have been put in a consistent state.
                            cache[key] = oldroot
                        else:
                            # Put result in a new link at the front of the
                            # queue.
                            last = root[PREV]
                            link = [last, root, key, result]
                            last[NEXT] = root[PREV] = cache[key] = link
                            _cache_vars[_FULL] = (len(cache) >= maxsize)
                        _cache_vars[_MISSES] += 1
                    return result

            def cache_info():
                """Report cache statistics"""
                with lock:
                    hits, misses = _cache_vars[:2]
                    return _CacheInfo(hits, misses, maxsize, len(cache))

            def cache_clear():
                """Clear the cache and cache statistics"""
                # nonlocal hits, misses, full
                with lock:
                    hits, misses, full, root = _cache_vars
                    cache.clear()
                    root[:] = [root, root, None, None]
                    hits = misses = 0
                    full = False
                    _cache_vars[:] = [hits, misses, full, root]

            wrapper.cache_info = cache_info
            wrapper.cache_clear = cache_clear
            return update_wrapper(wrapper, user_function)

        return decorating_function
