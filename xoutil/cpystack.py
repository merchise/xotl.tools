#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Utilities to inspect the CPython's stack.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_imports)

import inspect

from xoutil.eight import python_version
from xoutil.deprecation import deprecated


__all__ = ('MAX_DEEP', 'getargvalues', 'error_info',
           'object_info_finder', 'object_finder', 'track_value',
           'iter_stack', 'iter_frames')

MAX_DEEP = 25


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
    from xoutil.values.simple import force_sequence_coerce as array
    from xoutil.future.itertools import flatten
    pos, args, kwds, values = inspect.getargvalues(frame)
    res = {}
    for keys in pos:
        if keys:
            res.update({key: values[key] for key in flatten(array(keys))})
    if args:
        i = 0
        for item in values[args]:
            res['%s[%s]' % (args, i)] = item
            i += 1
    if kwds:
        res.update(values[kwds])
    return res


if python_version < 3:
    getargvalues.__doc__ += """
    In Python 2.7, packed arguments also works::

        >>> def nested((x, y), radius):
        ...    import sys
        ...    return getargvalues(sys._getframe())

        >>> nested((1, 2), 12)['y']
        2

    """


def __error_info(tb, *args, **kwargs):
    '''Internal function used by `error_info`:func: and
    `printable_error_info`:func:.

    '''
    # TODO: Formalize tests for this
    ALL = True
    res = []
    kwargs.update(dict.fromkeys(args, ALL))
    if kwargs:
        deep = 0
        processed = set()
        while tb and (deep < MAX_DEEP):
            frame = tb.tb_frame
            func_name = frame.f_code.co_name
            attrs1 = kwargs.get(func_name, None)
            attrs2 = kwargs.get(deep, None)
            if attrs1 or attrs2:
                processed.add(func_name)
                processed.add(deep)
                if (attrs1 is ALL) or (attrs2 is ALL):
                    attrs = ALL
                else:
                    attrs = list(attrs1) if attrs1 else []
                    if attrs2:
                        attrs.extend(attrs2)
                if attrs is ALL:
                    item = frame.f_locals.copy()
                else:
                    item = {key: frame.f_locals.get(key) for key in attrs}
                item['function-name'] = func_name
                item['traceback-deep'] = deep
                item['line-number'] = tb.tb_lineno
                item['file-name'] = frame.f_code.co_filename
                res.append(item)
            tb = tb.tb_next
            deep += 1
        for item in processed:
            if item in kwargs:
                del kwargs[item]
        if kwargs:
            res['unprocessed-items'] = kwargs
    return res


def error_info(*args, **kwargs):
    '''Get error information in current trace-back.

    No all trace-back are returned, to select which are returned use:

      - ``args``: Positional parameters

        - If string, represent the name of a function.

        - If an integer, a trace-back level.

        Return all values.

      - ``kwargs``: The same as ``args`` but each value is a list of local
        names to return. If a value is ``True``, means all local variables.

    Return a list with a dict in each item.

    Example::

      >>> def foo(x):
      ...     x += 1//x
      ...     if x % 2:
      ...         bar(x - 1)
      ...     else:
      ...         bar(x - 2)

      >>> def bar(x):
      ...     x -= 1//x
      ...     if x % 2:
      ...         foo(x//2)
      ...     else:
      ...         foo(x//3)

      >>> try:    # doctest: +SKIP
      ...     foo(20)
      ... except:
      ...     print(printable_error_info('Example', foo=['x'], bar=['x']))
      Example
         ERROR: integer division or modulo by zero
         ...

    '''
    import sys
    _error_type, _error, tb = sys.exc_info()
    return __error_info(tb, *args, **kwargs)


def printable_error_info(base, *args, **kwargs):
    '''Get error information in current trace-back.

    No all trace-back are returned, to select which are returned use:

      - ``args``: Positional parameters

        - If string, represent the name of a function.

        - If an integer, a trace-back level.

        Return all values.

      - ``kwargs``: The same as ``args`` but each value is a list of local
        names to return. If a value is ``True``, means all local variables.

    Return a formatted string with all information.

    See `error_info`:func: for an example.

    '''
    import sys
    _error_type, error, tb = sys.exc_info()
    if tb:
        res = '%s\n\tERROR: %s\n\t' % (base, error)
        info = __error_info(tb, *args, **kwargs)
        return res + '\n\t'.join(str(item) for item in info)
    else:
        return ''


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
            for key in d:
                value = d[key]
                if isinstance(value, obj_type):
                    res = (value, key, deep, frame)
            frame = frame.f_back
            deep += 1
        return res
    finally:
        del frame   # As recommended in the Python's doc to avoid memory leaks


def object_finder(obj_type, arg_name=None, max_deep=MAX_DEEP):
    '''Find an object of the given type through all arguments in stack frames.

    The difference with `object_info_finder`:func: is that this function
    returns the object directly, not a tuple.

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
        for _key in ctx:
            _value = ctx[_key]
            if (type(value) == type(_value)) and (value == _value):
                res = (ctx, _key)
        frame = frame.f_back
        deep += 1
    return res


def iter_stack(max_deep=MAX_DEEP):
    '''Iterates through stack frames until exhausted or `max_deep` is reached.

    To find a frame fulfilling a condition use::

      frame = next(f for f in iter_stack() if condition(f))

    .. versionadded:: 1.6.8

    '''
    # Using the previous pattern, functions `object_info_finder`,
    # `object_finder` and `track_value` can be reprogrammed or deprecated.

    frame = inspect.currentframe()
    try:
        deep = 0
        while (deep < max_deep) and (frame is not None):
            yield frame
            frame = frame.f_back
            deep += 1
    finally:
        del frame   # As recommended in the Python's doc to avoid memory leaks


@deprecated(iter_stack)
def iter_frames(max_deep=MAX_DEEP):
    '''Iterates through all stack frames.

    Returns tuples with the following::

        (deep, filename, line_no, start_line).

    .. versionadded:: 1.1.3

    .. deprecated:: 1.6.8 The use of params `attr_filter` and `value_filter`.

    '''
    # TODO: @manu Use this in all previous functions with same structure
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


del deprecated
