#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# untitled.py
#----------------------------------------------------------------------
# Copyright (c) 2011, 2012 Merchise Autrement
# All rights reserved.
#
# Author: Manuel Vázquez Acosta <mva.led@gmail.com>
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2011-11-08

"Several util functions for iterators"

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)


from functools import partial

from xoutil.types import is_scalar, Unset


__docstring_format__ = 'rst'
__version__ = '0.1.0'
__author__ = 'Manuel Vázquez Acosta <mva.led@gmail.com>'



def first(pred, iterable, default=None):
    '''
    Returns the first element of an iterable that matches pred.

    Examples::

        >>> first(lambda x: x > 4, range(10))
        5

        >>> first(lambda x: x < 4, range(10))
        0

    If nothing matches the default is returned::

        >>> first(lambda x: x > 100, range(10), False)
        False

    The iterable gets consumed if possible::

        >>> x = (x for x in range(10))
        >>> first(lambda x: x > 4, x)
        5

        >>> first(lambda x: x > 4, x)
        6

        >>> list(x)
        [7, 8, 9]
    '''
    return next((x for x in iterable if pred(x)), default)


def get_first(iterable):
    'Returns the first element of an iterable.'
    # TODO: Check who is using this function to find out if could be replaced
    #       by "next" and remove this one.
    #
    #    Response: `next` does not work on simple sequences::
    #        >>> get_first(range(10))
    #        0
    #        >>> next(range(10))
    #        Traceback (...)
    #            ...
    #        TypeError: list object is not an iterator
    return first(lambda x: True, iterable)


def flatten(sequence, is_scalar=is_scalar, depth=None):
    '''
    Flattens out a sequence. It takes care of everything deemed a collection
    (i.e, not a scalar according to the callabled passed in `is_scalar`)::

        >>> tuple(flatten((1, range(2, 5), xrange(5, 10))))
        (1, 2, 3, 4, 5, 6, 7, 8, 9)

        >>> def fib(n):
        ...     if n <= 1:
        ...         return 1
        ...     else:
        ...         return fib(n-2) + fib(n-1)

        >>> list(flatten((range(4), (fib(n) for n in range(3)))))
        [0, 1, 2, 3, 1, 1, 2]

    If `depth` is None the collection is flattened recursiverly until the
    "bottom" is reached. If `depth` is an integer then the collection is
    flattened up to that level::

        # depth=0 means simply not to flatten.
        >>> tuple(flatten((range(2), range(2, 4)), depth=0))
        ([0, 1], [2, 3])

        # But notice that depth=0 would not "explode" internal generators:
        >>> tuple(flatten((xrange(2), range(2, 4)), depth=0))
        (xrange(2), [2, 3])

        >>> tuple(flatten((xrange(2), range(2, 4),
        ...       (xrange(n) for n in range(5, 8))), depth=1))
        (0, 1, 2, 3, xrange(5), xrange(6), xrange(7))

    '''
    for item in sequence:
        if is_scalar(item):
            yield item
        elif depth == 0:
            yield item
        else:
            for subitem in flatten(item, is_scalar,
                                   depth=(depth - 1) if depth is not None
                                                     else None):
                yield subitem


def get_flat_list(sequence):
    '''
    Flatten out a sequence as a flat list.

    This is the same as::

        list(flatten(sequence))

    '''
    return list(flatten(sequence))


def dict_update_new(target, source):
    '''
    Update values in "source" that are new (not currently present) in "target".
    '''
    for key in source:
        if key not in target:
            target[key] = source[key]


def fake_dict_iteritems(source):
    '''
    Iterate (key, value) in a source that have defined method "keys" and
    operator "__getitem__".
    '''
    for key in source.keys():
        yield key, source[key]


def smart_dict(defaults, *sources):
    '''
    Build a dictionary looking in sources for all keys or attributes defined in
    "defaults".

    Each source could be a dictionary or any other object.

    Persistence of all original objects are warranted.
    '''
    from copy import deepcopy
    from collections import Mapping
    res = {}
    for key in defaults:
        for source in sources:
            get = source.get if isinstance(source, Mapping) else partial(getattr, source)
            value = get(key, Unset)
            if (value is not Unset) and (key not in res):
                res[key] = deepcopy(value)
        if key not in res:
            res[key] = deepcopy(defaults[key])
    return res



def slides(iterator, width=2, fill=Unset):
    '''
    Creates a sliding window of a given `width` over an iterable::

        >>> list(slides(range(1, 11)))
        [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]

    If the iterator does not yield a width-aligned number of items, the last
    slice returned is filled with `fill` (by default
    :class:`~xoutil.types.Unset`)::

        >>> list(slides(range(1, 11), width=3))   # doctest: +ELLIPSIS
        [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, <class '...Unset'>, <class '...Unset'>)]
    '''
    pos = 0
    res = []
    iterator = iter(iterator)
    current = next(iterator, Unset)
    while current is not Unset:
        if pos < width:
            res.append(current)
            current = next(iterator, Unset)
            pos = pos + 1
        else:
            yield tuple(res)
            res = []
            pos = 0
    if res:
        while pos < width:
            res.append(fill)
            pos += 1
        yield tuple(res)
