# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.cpystack
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# Copyright (c) 2009-2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#

'''Utilities to inspect the CPython's stack.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

import inspect

from xoutil.names import strlist as strs
from xoutil.compat import py3k as _py3k


__all__ = strs('MAX_DEEP', 'getargvalues', 'object_info_finder',
               'object_finder', 'track_value', 'iter_frames')
del strs

MAX_DEEP = 15


def getargvalues(frame):
    '''Inspects the given frame for arguments and returns a dictionary that
    maps parameters names to arguments values. If an `*` argument was passed
    then the key on the returning dictionary would be formatted as
    `<name-of-*-param>[index]`.

    For example in the function::

        >>> def autocontained(a, limit, *margs, **ks):
        ...    import sys
        ...    return getargvalues(sys._getframe())

        >>> autocontained(1, 12)['limit']
        12

        >>> autocontained(1, 2, -10, -11)['margs[0]']
        -10

    '''
    from xoutil.types import is_collection
    from xoutil.iterators import flatten
    pos, args, kwds, values = inspect.getargvalues(frame)
    res = {}
    for keys in pos:
        if not is_collection(keys):
            keys = (keys,)
        res.update({key: values[key] for key in flatten(keys)})
    if args:
        i = 0
        for item in values[args]:
            res['%s[%s]' % (args, i)] = item
            i += 1
    if kwds:
        res.update(values[kwds])
    return res

if not _py3k:
    getargvalues.__doc__ += """
    In Python 2.7, packed arguments also works::

        >>> def nested((x, y), radius):
        ...    import sys
        ...    return getargvalues(sys._getframe())

        >>> nested((1, 2), 12)['y']
        2

    """


def object_info_finder(obj_type, arg_name=None, max_deep=MAX_DEEP):
    '''Find an object of the given type through all arguments in stack frames.

    Returns a tuple with the following values:
        (arg-value, arg-name, deep, frame).

    When no object is found
    None is returned.

    Arguments:
        object_type: a type or a tuple of types as in "isinstance".
        arg_name: the arg_name to find; if None find in all arguments
        max_deep: the max deep to enter in the stack frames.

    '''
    frame = inspect.currentframe()
    try:
        deep = 0
        res = None
        while (res is None) and (deep < max_deep) and (frame is not None):
            ctx = getargvalues(frame)
            d = {arg_name: ctx.get(arg_name)} if arg_name is not None else ctx
            for key, value in d.iteritems():
                if isinstance(value, obj_type):
                    res = (value, key, deep, frame)
            frame = frame.f_back
            deep += 1
        return res
    finally:
        del frame   # As recommended in the Python's doc to avoid memory leaks


def object_finder(obj_type, arg_name=None, max_deep=MAX_DEEP):
    '''Use :func:`object_info_finder` to find an object of the given type
    through all arguments in stack frames.

    The difference is that this function return the object directly, not a
    tuple.

    '''
    finder = object_info_finder(obj_type, arg_name, max_deep)
    info = finder()
    return info[0] if info else None


def track_value(value, max_deep=MAX_DEEP):
    '''Find a value through all arguments in stack frames.

    Returns a dictionary with the full-context in the same level as "value".

    '''
    frame = inspect.currentframe().f_back.f_back
    deep = 0
    res = None
    while (res is None) and (deep < max_deep) and (frame is not None):
        ctx = getargvalues(frame)
        for _key, _value in ctx.iteritems():
            if (type(value) == type(_value)) and (value == _value):
                res = (ctx, _key)
        frame = frame.f_back
        deep += 1
    return res


def iter_frames(max_deep=MAX_DEEP):
    '''Iterates through all stack frames.

    Returns tuples with the following::

        (deep, filename, line_no, start_line).

    .. versionadded:: 1.1.3

    '''
    # TODO: [manu] Use this in all previous functions with same structure
    frame = inspect.currentframe()
    try:
        deep = 0
        while (deep < max_deep) and (frame is not None):
            yield (deep, frame.f_code.co_filename, frame.f_lineno,
                   frame.f_code.co_firstlineno, frame.f_locals)
            frame = frame.f_back
            deep += 1
    finally:
        del frame   # As recommended in the Python's doc to avoid memory leaks
