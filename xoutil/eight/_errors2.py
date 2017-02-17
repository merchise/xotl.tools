#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight._errors2
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-12-06

'''Exceptions handling, specific only for Python 2.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from . import _py3
assert not _py3, 'This module should not be loaded in Py3k'


def with_traceback(self, tb):
    '''set self.__traceback__ to tb and return self.'''
    self.__traceback__ = tb
    return self


def throw(self, *args, **kwds):
    from ._errors import get_args
    tb, cause = get_args(*args, **kwds)
    if not tb:
        # realize if a previous `with_traceback` was called.
        tb = getattr(self, '__traceback__', None)
    if tb:
        from types import TracebackType
        if not isinstance(tb, TracebackType):
            raise TypeError('__traceback__ must be a traceback or None')
    else:
        pass    # TODO: Look for trace-back in the calling stack
    if cause and not isinstance(cause, BaseException):
        raise TypeError('exception causes must derive from BaseException')
    self = with_traceback(self, tb)
    self.__cause__ = cause
    if tb:
        raise self, None, tb
    else:
        raise self
