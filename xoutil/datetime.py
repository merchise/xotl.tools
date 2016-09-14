#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.datetime
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Based on code submitted to comp.lang.python by Andrew Dalke, copied from
# Django and generalized.
#
# Created on Feb 15, 2012

'''Extends the standard `datetime` module.

- Python's ``datetime.strftime`` doesn't handle dates previous to 1900.
  This module define classes to override `date` and `datetime` to support the
  formatting of a date through its full proleptic Gregorian date range.

Based on code submitted to comp.lang.python by Andrew Dalke, copied from
Django and generalized.

You may use this module as a drop-in replacement of the standard library
`datetime` module.

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        # unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from xoutil.future.datetime import *    # noqa
from xoutil.deprecation import deprecated

import warnings    # noqa
warnings.warn('"xoutil.datetime" is now deprecated and it will be removed.'
              ' Use "xoutil.future.datetime" instead.', stacklevel=2)
del warnings


@deprecated(assure)
def new_date(d):
    '''Generate a safe date from a legacy datetime date object.'''
    return date(d.year, d.month, d.day)


@deprecated(assure)
def new_datetime(d):
    '''Generate a safe datetime give a legacy date or datetime object.'''
    args = [d.year, d.month, d.day]
    if isinstance(d, datetime.__base__):    # legacy datetime
        args.extend([d.hour, d.minute, d.second, d.microsecond, d.tzinfo])
    return datetime(*args)

del deprecated
