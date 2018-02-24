#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Extensions to the `functools` module from the Python's standard library.

You may use this module as drop-in replacement of `functools`.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

from functools import *    # noqa
import functools as _stdlib    # noqa

from xoutil.deprecation import deprecate_linked
deprecate_linked()
del deprecate_linked

from xoutil.eight import python_version    # noqa
from xoutil.eight import callable    # noqa

import xoutil.fp.tools as fp
from xoutil.deprecation import deprecated


@deprecated(fp.pos_args)
class ctuple(fp.pos_args):
    '''Simple tuple marker for `compose`:func:.

    Since is a callable you may use it directly in ``compose`` instead of
    changing your functions to returns ctuples instead of tuples::

       >>> def compat_print(*args):
       ...     for arg in args:
       ...         print(arg)

       >>> compose(compat_print, ctuple, list, range, math=False)(3)
       0
       1
       2

       # Without ctuple prints the list
       >>> compose(compat_print, list, range, math=False)(10)
       [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    .. deprecated:: 1.8.0 Use `xoutil.fp.tool.pos_args`:class:.

    '''


# TODO: [med]  Should we port the `ctuple` to fp.tools?
@deprecated(fp.compose)
def compose(*callables, **kwargs):
    '''Returns a function that is the composition of several `callables`.

    By default `compose` behaves like mathematical function composition: this
    is to say that ``compose(f1, ... fn)`` is equivalent to ``lambda _x:
    fn(...(f1(_x))...)``.

    If any "intermediate" function returns a `ctuple`:class: it is expanded as
    several positional arguments to the next function.

    .. versionchanged:: 1.5.5 At least a callable must be passed, otherwise a
                        TypeError is raised.  If a single callable is passed
                        it is returned without change.

    :param math: Indicates if `compose` should behave like mathematical
                 function composition: last function in `funcs` is applied
                 last. If False, then the last function in `func` is applied
                 first.

    .. deprecated:: 1.8.0 Use `xoutil.fp.tools.compose`:class:.

    '''
    from xoutil.params import check_count
    check_count(callables, 1, caller='compose')
    if not all(callable(func) for func in callables):
        raise TypeError('Every func must a callable')
    if len(callables) == 1:
        return callables[0]
    math = kwargs.get('math', True)
    if not math:
        callables = list(reversed(callables))

    return fp.compose(*reversed(callables))


# TODO: Check relevance of the following function.
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
       TypeError: power() takes at least 2 arguments (1 given)

    '''
    from xoutil.params import check_count
    from xoutil.fp.tools import compose
    check_count(args, 2, caller='power')
    funcs, times = args[:-1], args[-1]
    if any(not callable(func) for func in funcs):
        raise TypeError('Arguments of `power`, but last, must be callables')
    if not (isinstance(times, int) and times > 0):
        raise TypeError('Last argument of `power` must be a positive integer')
    if len(funcs) > 1:
        base = (compose(funcs), )
    else:
        base = (funcs[0], )
    return compose(*(base * times))


def lwraps(*args, **kwargs):
    '''Lambda wrapper.

    Useful for decorate lambda functions with name and documentation.

    As positional arguments could be passed the function to be decorated and
    the name in any order.  So the next two ``identity`` definitions are
    equivalents::

      >>> from xoutil.future.functools import lwraps as lw

      >>> identity = lw('identity', lambda arg: arg)

      >>> identity = lw(lambda arg: arg, 'identity')

    As keyword arguments could be passed some special values, and any number
    of literal values to be assigned:

    - **name**: The name of the function (``__name__``); only valid if not
      given as positional argument.

    - **doc**: The documentation (``__doc__`` field).

    - **wrapped**: An object to extract all values not yet assigned.  These
      values are ('__module__', '__name__' and '__doc__') to be assigned, and
      '__dict__' to be updated.

    If the function to decorate is present in the positional arguments, this
    same argument function is directly returned after decorated; if not a
    decorator is returned similar to standard `wraps`:func:.

    For example::

      >>> from xoutil.future.functools import lwraps as lw

      >>> is_valid_age = lw('is-valid-human-age', lambda age: 0 < age <= 120,
      ...                   doc=('A predicate to evaluate if an age is '
      ...                        'valid for a human being.')

      >>> @lw(wrapped=is_valid_age)
      ... def is_valid_working_age(age):
      ...     return 18 < age <= 70

      >>> is_valid_age(16)
      True

      >>> is_valid_age(200)
      False

      >>> is_valid_working_age(16)
      False

    .. versionadded:: 1.7.0

    '''
    from types import FunctionType, MethodType
    from xoutil.symbols import Unset
    from xoutil.eight import string_types, iteritems
    from xoutil.eight import string
    from xoutil.params import check_count

    def repeated(name):
        msg = "lwraps got multiple values for argument '{}'"
        raise TypeError(msg.format(name))

    def settle_str(name, value):
        if value is not Unset:
            if isinstance(value, string_types):
                if name not in source:
                    source[name] = value
                else:
                    repeated(name)
            else:
                from xoutil.eight import type_name
                msg = 'lwraps expecting string for "{}", {} found'
                raise TypeError(msg.format(name, type_name(value)))

    methods = (staticmethod, classmethod, MethodType)
    decorables = methods + (FunctionType, )

    name_key = '__name__'
    doc_key = '__doc__'
    mod_key = '__module__'
    safes = {name_key, mod_key}
    source = {}
    target = Unset
    count = len(args)
    check_count(count, 0, 2, caller='lwraps')
    i = 0
    while i < count:
        arg = args[i]
        if isinstance(arg, string_types):
            settle_str(name_key, arg)
        elif isinstance(arg, decorables):
            if target is Unset:
                target = arg
            else:
                repeated('target-function')
        else:
            msg = 'lwraps arg {} must be a string or decorable function'
            raise TypeError(msg.format(i))
        i += 1
    wrapped = kwargs.pop('wrapped', Unset)
    settle_str(name_key, kwargs.pop('name', Unset))
    settle_str(name_key, kwargs.pop(name_key, Unset))
    settle_str(doc_key, kwargs.pop('doc', Unset))
    settle_str(doc_key, kwargs.pop(doc_key, Unset))
    source.update(kwargs)
    if wrapped is not Unset:
        # TODO: Check the type of `wrapped` to find these attributes in
        # disparate callable objects similarly with functions.
        for name in (mod_key, name_key, doc_key):
            if name not in source:
                source[str(name)] = getattr(wrapped, name)
        d = source.setdefault('__dict__', {})
        d.update(wrapped.__dict__)

    def wrapper(target):
        if isinstance(target, decorables):
            res = target
            if isinstance(target, methods):
                target = target.__func__
            for name in (mod_key, name_key, doc_key):
                if name in source:
                    value = source.pop(name)
                    if name in safes:
                        value = string.force(value)
                    setattr(target, str(name), value)
                d = source.pop('__dict__', Unset)
                if d:
                    target.__dict__.update(d)
            for key, value in iteritems(source):
                setattr(target, key, value)
            return res
        else:
            from xoutil.eight import type_name
            msg = 'only functions are decorated, not {}'
            raise TypeError(msg.format(type_name(target)))

    return wrapper(target) if target else wrapper

    # TODO: Next code could be removed.
    # func.__name__ = string.force(name)
    # if doc:
    #     func.__doc__ = doc
    # return func


try:
    from functools import _CacheInfo
except ImportError:
    from xoutil.future.collections import namedtuple

    _CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize",
                                          "currsize"])

if python_version < 3.3:
    from threading import RLock
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
        return partial(update_wrapper, wrapped=wrapped,    # noqa
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
        sentinel = object()        # unique object used to signal cache misses
        make_key = _make_key       # build a key from the function arguments
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
                    # Simple caching without ordering or size limit nonlocal
                    # hits, misses
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
                    # nonlocal root, hits, misses, full
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
                            # TODO: never used
                            oldresult = root[RESULT]    # noqa
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


def curry(f):
    '''Return a function that automatically 'curries' is positional arguments.

    Example::

        >>> add = curry(lambda x, y: x + y)
        >>> add(1)(2)
        3

        >>> add(1, 2)
        3

        >>> add()()()(1, 2)
        3
    '''
    from xoutil.future.inspect import getfullargspec
    fargs = getfullargspec(f)[0]

    def curried(cargs=None):
        if cargs is None:
            cargs = []

        def inner(*args, **kwargs):
            cargs_ = cargs + list(args)
            if len(cargs_) < len(fargs):
                return curried(cargs_)
            else:
                return f(*cargs_, **kwargs)
        return inner
    return curried()
