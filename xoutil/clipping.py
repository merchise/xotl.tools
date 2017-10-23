#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''doc

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)

from xoutil.eight import python_version    # noqa


#: Value for `max_width` parameter in functions that reduce strings, must not
#: be less than this value.
MIN_WIDTH = 8

#: Default value for `max_width` parameter in functions that reduce strings,
#: see `crop`:func: and `small`:func:.
DEFAULT_MAX_WIDTH = 64

ELLIPSIS_ASCII = '...'
ELLIPSIS_UNICODE = '…'

#: Value used as a fill when a string representation is brimmed over.
ELLIPSIS = ELLIPSIS_UNICODE if python_version == 3 else ELLIPSIS_ASCII


def _check_max_width(max_width, caller=None):
    '''Used internally by some functions.'''
    if max_width is None:
        max_width = DEFAULT_MAX_WIDTH
    elif max_width < MIN_WIDTH:
        msg = '{}() '.format(caller) if caller else ''
        msg += ('invalid value for `max_width`, must be between greated than '
                '{}; got {}').format(MIN_WIDTH, max_width)
        raise ValueError(msg)
    return max_width


def crop(obj, max_width=None):
    '''Return a reduced string representation of `obj`.

    Classes can now define a new special method or attribute named
    '__crop__'.

    If `max_width` is not given, defaults to ``DEFAULT_MAX_WIDTH``.

    .. versionadded:: 1.8.0

    '''
    from xoutil.eight import callable, type_name, string_types
    max_width = _check_max_width(max_width, caller='crop')
    if isinstance(obj, string_types):
        res = obj    # TODO: reduce
    elif hasattr(obj, '__crop__'):
        aux = obj.__crop__
        if isinstance(aux, string_types):
            res = aux
        elif callable(aux):
            if getattr(aux, '__self__', 'ok') is not None:
                res = aux()
            else:
                res = None
        else:
            msg = "crop() invalid '__crop__' type: {}"
            raise TypeError(msg.format(type_name(aux)))
    else:
        res = None
    if res is None:
        res = _crop(obj, max_width)
    return res


def _crop(obj, max_width):
    '''Internal tool for `crop`:func:.'''
    from collections import Set, Mapping
    from xoutil.eight import type_name
    res = str(obj)
    if (res.startswith('<') and res.endswith('>')) or len(res) > max_width:
        try:
            res = obj.__name__
        except AttributeError:
            if isinstance(obj, (tuple, list, Set, Mapping)):
                res = crop_iterator(obj, max_width)
            else:
                res = '{}({})'.format(type_name(obj), ELLIPSIS)
    return res


def crop_iterator(obj, max_width=None):
    '''Return a reduced string representation of the iterator `obj`.

    See `crop`:func: function for a more general tool.

    If `max_width` is not given, defaults to ``DEFAULT_MAX_WIDTH``.

    .. versionadded:: 1.8.0

    '''
    from collections import Set, Mapping
    from xoutil.eight import type_name
    max_width = _check_max_width(max_width, caller='crop_iterator')
    classes = (tuple, list, Mapping, Set)
    cls = next((c for c in classes if isinstance(obj, c)), None)
    if cls:
        res = ''
        if cls is Set and not obj:
            borders = ('{}('.format(type_name(obj)), ')')
        else:
            borders = ('()', '[]', '{}', '{}')[classes.index(cls)]
            UNDEF = object()
            sep = ', '
            if cls is Mapping:
                from xoutil.eight import iteritems

                def itemrepr(item):
                    key, value = item
                    return '{}: {}'.format(repr(key), repr(value))
            else:
                iteritems = iter
                itemrepr = repr
            items = iteritems(obj)
            ok = True
            while ok:
                item = next(items, UNDEF)
                if item is not UNDEF:
                    if res:
                        res += sep
                    aux = itemrepr(item)
                    if len(res) + len(borders) + len(aux) <= max_width:
                        res += aux
                    else:
                        res += ELLIPSIS
                        ok = False
                else:
                    ok = False
        return '{}{}{}'.format(borders[0], res, borders[1])
    else:
        raise TypeError('crop_iterator() expects tuple, list, set, or '
                        'mapping; got {}'.format(type_name(obj)))


def small(obj, max_width=None):
    '''Crop the string representation of `obj` and make some replacements.

    - Lambda function representations ('<lambda>' by 'λ').

    - Ellipsis ('...'  by '…')

    If max_width is not given, defaults to ``DEFAULT_MAX_WIDTH``.

    .. versionadded:: 1.8.0

    '''
    max_width = _check_max_width(max_width, caller='small')
    res = crop(obj, max_width)
    res = res.replace(ELLIPSIS_ASCII, ELLIPSIS_UNICODE)
    res = res.replace((lambda: None).__name__, 'λ')
    return res
