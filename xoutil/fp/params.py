#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.fp.params
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created 2017-03-18

'''Tools for managing function arguments.

Function `issue_9137`:func: allow to parse positional arguments for methods
avoiding the conflict expressed in issue 9137.

Function `check_count`:func: allow to check positional arguments count against
lower and upper limits.

.. versionadded:: 1.7.0

.. versionchanged:: 1.8.0 Migrated to a completely new shape forgetting
       initial `xoutil.params` module.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import sys

#: The maximum number of positional arguments allowed when calling a function.
MAX_ARG_COUNT = sys.maxsize    # just any large number
del sys


from xoutil import Undefined    # used implicitly for absent default


def issue_9137(args):
    '''Parse arguments for methods, fixing issue 9137 (self ambiguity).

    There are methods that expect 'self' as valid keyword argument, this is
    not possible if this name is used explicitly::

        def update(self, *args, **kwds):
            ...

    To solve this, declare the arguments as ``method_name(*args, **kwds)``,
    and in the function code::

        self, args = issue_9137(args)

    :returns: (self, remainder positional arguments in a tuple)

    '''
    self = args[0]    # Issue 9137
    args = args[1:]
    return self, args


def check_count(args, low, high=MAX_ARG_COUNT, caller=None):
    '''Check the positional arguments actual count against constrains.

    :param args: The args to check count, normally is a tuple, but an integer
           is directly accepted.

    :param low: Integer expressing the minimum count allowed.

    :param high: Integer expressing the maximum count allowed.

    :param caller: Name of the function issuing the check, its value is used
           only for error reporting.

    '''
    assert isinstance(low, int) and low >= 0
    assert isinstance(high, int) and high >= low
    if isinstance(args, int):
        count = args
        if count < 0:
            msg = "check_count() don't accept a negative argument count: {}"
            raise ValueError(msg.format(count))
    else:
        count = len(args)
    if count < low:
        error = True
        adv = 'exactly' if low == high else 'at least'
        if low == 1:
            aux = '{} one argument'.format(adv)
        else:
            aux = '{} {} arguments'.format(adv, low)
    elif count > high:
        error = True
        if low == high:
            if low == 0:
                aux = 'no arguments'
            elif low == 1:
                aux = 'exactly one argument'
            else:
                aux = 'exactly {} arguments'.format(low)
        elif high == 1:
            aux = 'at most one argument'
        else:
            aux = 'at most {} arguments'.format(high)
    else:
        error = False
    if error:
        if caller:
            name = '{}()'.format(caller)
        else:
            name = 'called function or method'
        raise TypeError('{} takes {} ({} given)'.format(name, aux, count))


def check_default(absent=Undefined):
    '''Get a default value passed as a last excess positional argument.

    :param absent: The value to be used by default if no one is given.
           Defaults to `~xoutil.Undefined`:obj:.

    For example::

        def get(self, name, *default):
            from xoutil.fp.tools import check_default, Undefined
            if name in self.inner_data:
                return self.inner_data[name]
            elif check_default()(*default) is not Undefined:
                return default[0]
            else:
                raise KeyError(name)

    '''
    def default(res=absent):
        return res
    return default
