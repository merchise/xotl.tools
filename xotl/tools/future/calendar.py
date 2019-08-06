#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""Extends the standard `calendar` module.

xotl.tools extensions:

- Settle constants for all months.

Original documentation:

"""

from calendar import *  # noqa
import calendar as _stdlib  # noqa

__doc__ += _stdlib.__doc__

try:
    __all__ = list(_stdlib.__all__)
except AttributeError:
    pass


(
    January,
    February,
    March,
    April,
    May,
    June,
    July,
    August,
    September,
    October,
    November,
    December,
) = range(1, 13)
