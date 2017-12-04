#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Complements for object string representation protocol.

There are contexts that using ``str`` or ``repr`` protocol would be inadequate
because shorter string representations are expected (e.g. formatting recursive
objects in `pprint`:mod: standard module that they have a new Boolean
parameter in Python 3 named ``compact``).

There is a protocol to complement operators used by standard string
representation functions (``__str__``, ``__repr__``) by defining a new one
with name ``__crop__``.  This operator will receive some extra parameters with
default values, see `crop`:func: function for details.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)

from xoutil.eight import python_version    # noqa


#: Value for `max_width` parameter in functions that shorten strings, must not
#: be less than this value.
MIN_WIDTH = 8

#: Default value for `max_width` parameter in functions that shorten strings,
#: see `crop`:func:.
DEFAULT_MAX_WIDTH = 64

ELLIPSIS_ASCII = '...'
ELLIPSIS_UNICODE = '…'

#: Value used as a fill when a string representation overflows.
ELLIPSIS = ELLIPSIS_UNICODE if python_version == 3 else ELLIPSIS_ASCII

#: Operator name allowing objects to define theirs own method for string
#: shortening.
OPERATOR_NAME = '__crop__'

_LAMBDA_NAME = (lambda: 0).__name__


def _check_max_width(max_width, caller=None):
    '''Type constrain for "max_width" parameter.'''
    if max_width is None:
        max_width = DEFAULT_MAX_WIDTH
    elif max_width < MIN_WIDTH:
        msg = '{}() '.format(caller) if caller else ''
        msg += ('invalid value for `max_width`, must be between greated than '
                '{}; got {}').format(MIN_WIDTH, max_width)
        raise ValueError(msg)
    return max_width


def crop(obj, max_width=None, canonical=False):
    '''Return a reduced string representation of `obj`.

    Classes can now define a new special attribute ``__crop__``.  It
    can be a `string <str>`:class: (or `unicode`:class: in Python 2).  Or a
    method::

       def __crop__(self, max_width=None, canonical=False):
           pass

    If the `obj` does not implement the ``__crop__`` protocol, a standard one
    is computed.

    :param max_width: Maximum length for the resulting string.  If is not
           given, defaults to `DEFAULT_MAX_WIDTH`:obj:.

    :param canonical: If True `repr`:func: protocol must be used instead
           `str`:func: (the default).

    .. versionadded:: 1.8.0

    '''
    from functools import partial
    from xoutil.eight import callable, type_name, string_types
    max_width = _check_max_width(max_width, caller='crop')
    if isinstance(obj, string_types):
        res = obj    # TODO: reduce
    else:
        oper = getattr(obj, OPERATOR_NAME, partial(_crop, obj))
        if isinstance(oper, string_types):
            # XXX: Allowing to define expecting operator as a static resulting
            # string
            res = oper
        elif callable(oper):
            # XXX: I don't remember anymore why this check is needed
            if getattr(oper, '__self__', 'OK') is not None:
                try:
                    res = oper(max_width=max_width, canonical=canonical)
                except TypeError:
                    # Just preventing operator definition with no extra
                    # parameters
                    res = oper()
            else:
                res = NotImplemented
        else:
            msg = "crop() invalid '{}' type: {}"
            raise TypeError(msg.format(OPERATOR_NAME, type_name(oper)))
    return res


def _crop(obj, max_width=None, canonical=False):
    '''Internal crop tool.'''
    from collections import Set, Mapping
    from xoutil.eight import type_name
    res = repr(obj) if canonical else str(obj)
    if (res.startswith('<') and res.endswith('>')) or len(res) > max_width:
        try:
            res = obj.__name__
            if res == _LAMBDA_NAME and not canonical and python_version == 3:
                # Just a gift
                res = res.replace(_LAMBDA_NAME, 'λ')
        except AttributeError:
            if isinstance(obj, (tuple, list, Set, Mapping)):
                res = crop_iterator(obj, max_width, canonical)
            else:
                res = '{}({})'.format(type_name(obj), ELLIPSIS)
    return res


def crop_iterator(obj, max_width=None, canonical=False):
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


# aliases
short = small = crop    # noqa
