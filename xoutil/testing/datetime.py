#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from hypothesis import strategies


dates = strategies.dates
maybe_date = dates() | strategies.none()


@strategies.composite
def timespans(draw, unbounds='any'):
    '''A strategy that generates `xoutil.future.datetime.TimeSpan`.


    '''
    from xoutil.future.datetime import TimeSpan
    date1 = draw(maybe_date if unbounds in ('any', 'past') else dates())
    date2 = draw(maybe_date if unbounds in ('any', 'future') else dates())
    if date1 and date2:
        start1 = min(date1, date2)
        end1 = max(date1, date2)
    else:
        start1 = date1
        end1 = date2
    return TimeSpan(start_date=start1, end_date=end1)
