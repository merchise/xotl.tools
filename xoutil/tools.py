#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Simple tools minimizing dependencies on other modules.

The only used modules are Python's standard library `re`:mod:, and
`xoutil.eight`:mod:.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

from xoutil.deprecation import deprecated
from xoutil.params import check_default


# TODO: review this
def nameof(obj):
    '''Give the name of an object.

    First try normally named object (those having a ``'__name__'`` attribute);
    then some special classes instances that wraps the name internally are
    checked; then it tests for some objects that are singletons\ [#sing]_;
    finally -as a default tentative- return the type name.

    For example::

      >>> nameof(object)
      'object'

      >>> nameof(lambda x: x)
      '<lambda>'

      >>> singletons = (None, True, False, Ellipsis, NotImplemented)
      >>> [nameof(s) for s in singletons]
      ['None', 'True', 'False', 'Ellipsis', 'NotImplemented']

      >>> nameof(0)
      'int'

    This is a beginning intended to deprecate a "fauna" of several existing
    functions with the same purpose around several modules.

    .. [#sing] In this case an object is considered a signgleton if both of
               its representation strings (``str(obj)`` and ``repr(obj)``)
               match and it is a valid identifier.

    '''
    try:
        return obj.__name__
    except AttributeError:
        if isinstance(obj, (staticmethod, classmethod)):
            return obj.__func__.__name__
        else:    # try for singleton
            import re
            res = str(obj)
            identifier_regex = '(?i)^[_a-z][_a-z0-9]*$'    # TODO: Py3?
            if res == repr(obj) and re.match(identifier_regex, res):
                return res
            else:
                from xoutil.eight import typeof
                return typeof(obj).__name__


# TODO: Move all functions in this module to a new place

@deprecated(check_default)
def get_default(args, default=None):
    '''Get a default value passed as last positional argument.

    See `xoutil.params.check_default`:func: for a more accurate function that
    replace this.

    .. deprecated:: 1.8.0

    '''
    return check_default(default)(*args)


def args_repr(args, **options):
    '''Format positional arguments to use in exception handling.

    :params args: tuple as obtained in arguments when declared in a function
           as ``*args``.

    :param options: some extra options could be used as excess keyword
           arguments.

           - count: maximum amount of actual parameters to process; after
             reached that amount a tail item is appended with the remainder
             number.  If None is given -the default- the value ``3`` is used.

           - cast: must be a function to convert the value into the
             representation; when no value is given -the default- it's assumed
             ``λ arg: type(arg).__name__``.

           - item_format: the format for each argument type, if no value is
             given the value "{}" is used.  Each item is obtained as with the
             "cast" function.

           - tail_format: a format string for the tail with the remainder (not
             processed arguments) specification; must contain a positional
             (like "{}") format specifier if obtaining the remainder count is
             desired; when no value is given -the default- the value "..." is
             used; another valid example could be "and {} more".

           - joiner: could be a function or a string to join all parts
             including the tail; if no value is given -the default- the value
             ", " is used (thed equivalent to ``', '.join``).

    For example::

      >>> args_repr((1, 2.0, "3", {}))
      'int, float, str, ...'

    '''
    from xoutil.eight import typeof, string_types
    count = options.get('count', 3)
    cast = options.get('cast', lambda arg: typeof(arg).__name__)
    item_format = options.get('item_format', '{}')
    tail_format = options.get('tail_format', '...')
    joiner = options.get('joiner', ', ')
    if isinstance(joiner, string_types):
        joiner = str(joiner).join
    parts = []
    i = 0
    while i < min(count, len(args)):
        parts.append(item_format.format(cast(args[i])))
        i += 1
    rem = len(args) - i
    if rem > 0:
        parts.append(tail_format.format(rem))
    return joiner(parts)


def kwargs_repr(kwargs, **options):
    '''Format positional arguments to use in exception handling.

    :params kwargs: dict as obtained in arguments when declared as
           ``**kwargs``.

    :param options: some extra options are used in this function.

           - count: maximum amount of actual parameters to process; after
             reached that amount a tail item is appended with the remainder
             number.  If None is given -the default- the value ``3`` is used.

           - cast: must be a function to convert the value into the
             representation; when no value is given -the default- it's assumed
             ``λ arg: type(arg).__name__``.

           - item_format: the format for each argument type, if no value is
             given the value "{}:{}" is used.  Each item value is
             obtained as with the "cast" function.

           - tail_format: a format string for the tail with the remainder (not
             processed arguments) specification; must contain a positional
             (like "{}") format specifier if obtaining the remainder count is
             desired; when no value is given -the default- the value "..." is
             used; another valid example could be "and {} more".

           - joiner: could be a function or a string to join all parts
             including the tail; if no value is given -the default- the value
             ", " is used (thed equivalent to ``', '.join``).

    For example::

      >>> kwargs_repr({'x': 1, 'y': 2.0, 'z': '3', 'zz': {}})
      'x:int, y:float, z:str, ...'

    '''
    from xoutil.eight import typeof, string_types
    count = options.get('count', 3)
    cast = options.get('cast', lambda arg: typeof(arg).__name__)
    item_format = options.get('item_format', '{}:{}')
    tail_format = options.get('tail_format', '...')
    joiner = options.get('joiner', ', ')
    if isinstance(joiner, string_types):
        joiner = str(joiner).join
    parts = []
    keys = list(kwargs)
    keys.sort()
    i = 0
    while i < min(count, len(keys)):
        key = keys[i]
        value = kwargs[key]
        parts.append(item_format.format(key, cast(value)))
        i += 1
    rem = len(keys) - i
    if rem > 0:
        parts.append(tail_format.format(rem))
    return joiner(parts)


def both_args_repr(args, kwargs, **options):
    '''Combine both argument kind representations.

    Both kinds are: positional (see `args_repr`:func:) and keyword (see
    `kwargs_repr`:func:).

    For example::

      >>> both_args_repr((1, 2.0, "3"), {'x': 1, 'y': 2.0, 'z': '3'})
      'int, float, str, x:int, y:float, z:str'

    '''
    from xoutil.eight import string_types
    joiner = options.get('joiner', ', ')
    if isinstance(joiner, string_types):
        joiner = str(joiner).join
    items = (args, args_repr), (kwargs, kwargs_repr)
    parts = [res for res in (fn(aux, **options) for aux, fn in items) if res]
    return joiner(parts)
