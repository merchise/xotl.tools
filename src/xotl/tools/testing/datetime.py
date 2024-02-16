#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from hypothesis import strategies


@strategies.composite
def timespans(draw, dates=None, unbounds="any", always_valid=True):
    """A strategy that generates `xotl.tools.future.datetime.TimeSpan`:class:.

    This is a `hypothesis`_ strategy.

    `dates` should be None or generator of `datetime.date`:class: objects.
    It defaults to `hypothesis.strategies.dates`:func:

    `unbounds` should be one of the strings 'none', 'any', 'past', 'future'.
    If 'any' then the generated time span can be `unbound
    <xotl.tools.future.datetime.TimeSpan.unbound>`:attr:.  If 'past' it can be
    unbound to the past.  If 'future', it can be unbound to the future.  If
    'none', the generated time span will always be bound.  In all cases that
    generate unbound time spans, we can also generate bound time spans.

    If `always_valid` is True all generated time spans will be `valid
    <xotl.tools.future.datetime.TimeSpan.valid>`:attr:.  Otherwise we may
    generate invalid ones.

    Usage::

       >>> from hypothesis import given
       >>> from xotl.tools.testing.datetime import timespans

       >>> @given(timespans())
       ... def test_timespan(ts):
       ...    pass

    .. _hypothesis: https://hypothesis.readthedocs.io/

    .. versionadded:: 1.8.2

    """
    from xotl.tools.future.datetime import TimeSpan

    if dates is None:
        dates = strategies.dates()
    maybe = strategies.none() | dates
    if unbounds in ("any", "past", "future", "none"):
        if unbounds in ("any", "past"):
            date1 = draw(maybe)
        else:
            date1 = draw(dates)
        if unbounds in ("any", "future"):
            date2 = draw(maybe)
        else:
            date2 = draw(dates)
    else:
        raise ValueError("unbounds should be one of 'any', 'past', or 'future'.")
    if date1 and date2 and always_valid:
        start1 = min(date1, date2)
        end1 = max(date1, date2)
    else:
        start1 = date1
        end1 = date2
    return TimeSpan(start_date=start1, end_date=end1)


@strategies.composite
def datetimespans(draw, dates=None, unbounds="any", always_valid=True):
    """A strategy that generates `xotl.tools.future.datetime.DateTimeSpan`:class:.

    This is a `hypothesis`_ strategy.

    `dates` should be None or generator of `datetime.datetime`:class: objects.
    It defaults to `hypothesis.strategies.datetimes`:func:

    `unbounds` should be one of the strings 'none', 'any', 'past', 'future'.
    If 'any' then the generated time span can be `unbound
    <xotl.tools.future.datetime.TimeSpan.unbound>`:attr:.  If 'past' it can be
    unbound to the past.  If 'future', it can be unbound to the future.  If
    'none', the generated time span will always be bound.  In all cases that
    generate unbound time spans, we can also generate bound time spans.

    If `always_valid` is True all generated time spans will be `valid
    <xotl.tools.future.datetime.TimeSpan.valid>`:attr:.  Otherwise we may
    generate invalid ones.

    Usage::

       >>> from hypothesis import given
       >>> from xotl.tools.testing.datetime import datetimespans

       >>> @given(datetimespans())
       ... def test_datetimespan(dts):
       ...    pass

    .. _hypothesis: https://hypothesis.readthedocs.io/

    .. versionadded:: 1.9.7

    """
    from xotl.tools.future.datetime import DateTimeSpan

    if dates is None:
        dates = strategies.datetimes()
    maybe = strategies.none() | dates
    if unbounds in ("any", "past", "future", "none"):
        if unbounds in ("any", "past"):
            date1 = draw(maybe)
        else:
            date1 = draw(dates)
        if unbounds in ("any", "future"):
            date2 = draw(maybe)
        else:
            date2 = draw(dates)
    else:
        raise ValueError("unbounds should be one of 'any', 'past', or 'future'.")
    if date1 and date2 and always_valid:
        start1 = min(date1, date2)
        end1 = max(date1, date2)
    else:
        start1 = date1
        end1 = date2
    return DateTimeSpan(start_datetime=start1, end_datetime=end1)
