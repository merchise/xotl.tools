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

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from ._throw import __doc__
from . import _py3
assert not _py3, 'This module should not be loaded in Python 3'


def throw(error, *args, **kwds):
    from ._throw import parse_args, force_traceback
    cause, tb = parse_args(args, kwds)
    if tb is None:
        tb = force_traceback(error, cause)
    if cause:
        if isinstance(cause, BaseException):
            error.__cause__ = cause
        else:
            raise TypeError('exception cause must derive from BaseException')
    error.__traceback__ = tb
    raise error, None, tb


throw.__doc__ = __doc__
