#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.future.calendar
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-06-29

'''Extends the standard `calendar` module.

Xoutil extensions:

- Settle constants for all months.

Original documentation:

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from calendar import *    # noqa
import calendar as _stdlib    # noqa

__doc__ += _stdlib.__doc__

try:
    __all__ = list(_stdlib.__all__)
except AttributeError:
    pass


def _get_month_name_list():
    import sys
    import locale
    try:
        locale.setlocale(locale.LC_TIME, ('en_US', 'UTF-8'))
        mod = sys.modules[__name__]
        month = 1
        while month <= 12:
            name = _stdlib.month_name[month]
            if not hasattr(mod, name):
                setattr(mod, name, month)
                month += 1
    finally:
        locale.resetlocale(locale.LC_TIME)



_get_month_name_list()

del _get_month_name_list
