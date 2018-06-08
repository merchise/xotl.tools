#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import absolute_import as _py3_abs_import


def update_context(self=None):
    import sys
    tb_name = '__traceback__'
    names = 'last_value', 'last_traceback'
    error, traceback = (getattr(sys, name, None) for name in names)
    if error is not None and not hasattr(error, tb_name):
        error.__traceback__ = traceback
    _, error, traceback = sys.exc_info()
    if error is not None and not hasattr(error, tb_name):
        error.__traceback__ = traceback
    if isinstance(self, BaseException):
        for name in ('__context__', '__cause__', tb_name):
            if not hasattr(self, name):
                setattr(self, name, None)


def set_context(error, traceback, cause):
    import sys
    context = sys.exc_info()[1]
    error.__context__ = None if context is error else context
    error.__cause__ = cause
    if traceback is not None:
        error.__traceback__ = traceback
    elif not hasattr(error, '__traceback__'):
        error.__traceback__ = None
    return error


def raise2(error, traceback, cause):
    set_context(error, traceback, cause)
    raise error, None, error.__traceback__


def get_info():
    import sys
    res = sys.exc_info()
    if res[0] is None:
        names = 'last_type', 'last_value', 'last_traceback'
        res = tuple(getattr(sys, name, None) for name in names)
    return res
