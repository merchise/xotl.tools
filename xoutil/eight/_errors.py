#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight._errors
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-02-16

'''Common internals for exceptions handling.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


def get_args(*args, **kwds):
    '''Common function to retrieve arguments for `throw`.
def get_cause(self):
    '''Get a  previous cause defined on an error.'''
    return getattr(self, '__cause__', None)


def get_tb(self):
    '''Get existing trace-back defined on an error.'''
    name = '__traceback__'
    res = getattr(self, name, None)
    if res is None:
        cause = get_cause(self)
        if cause:
            res = getattr(cause, name, None)
    return res


    count = len(args)
    if count < 3:
        tb = args[0] if count else None
        cause = args[1] if count == 2 else None
    else:
        msg = 'throw() takes at most 2 arguments ({} given)'
        raise TypeError(msg.format(count))
    if tb is None:
        names = ('tb', 'traceback', '__traceback__')
        tb = next((kwds.pop(name) for name in names if name in kwds), None)
    if cause is None:
        names = ('cause', '__cause__', 'from', 'from_')
        cause = next((kwds.pop(name) for name in names if name in kwds), None)
    if not kwds:
        return tb, cause
    else:
        msg = 'throw() got unexpected keyword arguments {}'
        raise TypeError(msg.format(tuple(kwds)))


throw_doc = \
    '''Unify syntax of Python 3 ``raise``.

    If you need new extensions, use this function instead of the `raise`
    statement.

    In addition to the exception instance itself, one or two extra parameters
    could be passed:

    :param traceback: to execute the ``raise error.with_traceback(tb)``
           Python 3 equivalent.

    :param cause: to execute the ``raise error from cause`` Python 3
           equivalent.

    When positional arguments are used, `traceback` must be the first and
    `cause` the second.

    Keyword arguments are the preferred syntax, several aliases are defined:

    - 'traceback': 'tb', and '__traceback__'.

    - 'cause': '__cause__', 'from_', and 'from'\ [1]_.

    .. [1] This is a reserved keyword, but it's include as an alias to allow
           its use when passing arguments in a dictionary as ``**d``.

    '''
