#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import absolute_import as _py3_abs_import

from xoutil.symbols import Unset


def _fix_context(error, **kwds):
    names = ('traceback', 'cause', 'context')
    i, count = 0, len(names)
    while i < count:
        name = '__{}__'.format(names[i])
        value = kwds.get(names[i], Unset)
        if value is not Unset:
            setattr(error, name, value)
            if isinstance(value, BaseException):
                _fix_context(value)
        elif not hasattr(error, name):
            setattr(error, name, None)
        i += 1


def raise2(error):
    raise error, None, error.__traceback__    # noqa
