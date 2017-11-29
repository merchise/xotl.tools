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


January = 1
February = 2
March = 3
April = 4
May = 5
June = 6
July = 7
August = 8
September = 9
October = 10
November = 11
December = 12
