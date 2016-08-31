#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.tools
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise and Contributors
# Copyright (c) 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created 2014-05-15

'''Simple tools with no dependencies on other modules.

Extensions to the Python's standard library.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)


def get_default(args, default=None):
    '''Get a default value passed as last positional argument.

    Several functions that get values define an optional default value
    parameter.  To use a construction ``def get_foobar(name, default=None)``
    sometimes is not possible because `None` could be a possible valid
    "foobar" value.  In these cases it's better to construct something like::

      def get_foobar(name, *default):
          ...

    and in client code you can call this function with a impossible "foobar"
    value, like: ``res = get_foobar('egg', Undefined)`` (see `xoutil.cl`).

    This function receive the tuple as received by the function, and which
    value to return if None is given::

      def get_foobar(name, *default):
          from xoutil.tools import get_default
          from xoutil import Undefined as _undef
          default = get_default(default, _undef)
          ...

    If tuple `args` has an invalid size, a `TypeError` exception is raised.

    '''
    count = len(args)
    if count == 0:
        return default
    elif count == 1:
        return args[0]
    else:
        raise TypeError("expected 0 or 1 values for default, got %s" % count)


def args_repr(args, **options):
    '''Format positional arguments to use in exception handling.

    :params args: tuple as obtained in arguments when declared as ``*args``.

    :param options: some extra options are used in this function.

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
    from xoutil.eight import type_name, string_types
    count = options.get('count', 3)
    cast = options.get('cast', lambda arg: type_name(arg))
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
    from xoutil.eight import type_name, string_types
    count = options.get('count', 3)
    cast = options.get('cast', lambda arg: type_name(arg))
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
