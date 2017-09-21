#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ----------------------------------------------------------------------
# xoutil.tests.test_datetime
# ----------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~°/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-03-25

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

import pytest

from xoutil.future.datetime import date
from xoutil.future.datetime import daterange
from xoutil.future.datetime import TimeSpan, EmptyTimeSpan

import hypothesis
from hypothesis import strategies, given


dates = strategies.dates
maybe_date = dates() | strategies.none()


@strategies.composite
def time_span(draw, unbounds='any'):
    date1 = draw(maybe_date if unbounds in ('any', 'past') else dates())
    date2 = draw(maybe_date if unbounds in ('any', 'future') else dates())
    if date1 and date2:
        start1 = min(date1, date2)
        end1 = max(date1, date2)
    else:
        start1 = date1
        end1 = date2
    return TimeSpan(start_date=start1, end_date=end1)


def test_daterange_stop_only():
    result = list(daterange(date(1978, 10, 21)))
    assert result[0] == date(1978, 10, 1)
    assert result[-1] == date(1978, 10, 20)


def test_daterange_empty():
    assert [] == list(daterange(date(1978, 10, 21), -2))
    assert [] == list(daterange(date(1978, 10, 21), date(1978, 10, 10)))
    assert [] == list(daterange(date(1978, 10, 10), date(1978, 10, 20), -1))


def test_daterange_going_back_in_time():
    result = list(daterange(date(1978, 10, 21), -2, -1))
    assert result[0] == date(1978, 10, 21)
    assert result[-1] == date(1978, 10, 20)


def test_daterange_invalid_int_stop():
    with pytest.raises(TypeError):
        daterange(10)


def test_daterange_invalid_step():
    with pytest.raises(ValueError):
        daterange(None, date(1978, 10, 21), 0)


@given(time_span(), time_span())
@hypothesis.example(ts1=TimeSpan(), ts2=time_span().example())
def test_intersection_commutable(ts1, ts2):
    # Commutable
    assert ts2 * ts1 == (ts1 & ts2)


@given(time_span(), time_span())
@hypothesis.example(ts1=TimeSpan(), ts2=time_span().example())
def test_intersection_containment(ts1, ts2):
    overlap = ts1 * ts2
    if overlap is not None:
        # The intersection must always be totally covered by both ts1 and ts2,
        # unless ts1 and ts2 don't intersect
        assert (overlap & ts1) == overlap
        assert (overlap <= ts1) is True
        assert (overlap <= ts2) is True


@given(time_span(), time_span())
@hypothesis.example(ts1=TimeSpan(), ts2=time_span().example())
def test_comparision(ts1, ts2):
    if ts1 <= ts2 <= ts1:
        assert ts1 == ts2
    if ts1 == ts2:
        assert ts1 <= ts2 <= ts1

    # Single day intersection and equality test
    if ts1.start_date:
        assert ts1 * ts1.start_date == ts1.start_date
        assert ts1.start_date in ts1

    # Single day union and equality test
    if ts1.start_date:
        assert ts1 + ts1.start_date == ts1


@given(time_span(), time_span())
@hypothesis.example(TimeSpan(), time_span().example())
def test_union_commutable(ts1, ts2):
    # Commutable and alias
    assert (ts2 | ts1) == (ts1 + ts2)


@given(time_span(), time_span())
@hypothesis.example(ts1=TimeSpan(), ts2=time_span().example())
def test_union_containment(ts1, ts2):
    union = ts1 + ts2
    if union is not None:
        # The union must always be cover both ts1 and ts2
        assert (ts1 <= union) is True
        assert (ts2 <= union) is True


@given(time_span(), time_span(), dates())
def test_general_cmp_properties(ts1, ts2, date):
    assert bool(ts1 <= ts2) == bool(ts2 >= ts1)
    # In Python 2, dates have a __le__ that does no compare to timespans.
    assert bool(TimeSpan.from_date(date) <= ts2) == bool(ts2 >= date)

    overlap = ts1 & ts2
    if not overlap:
        # Disjoint sets are not orderable...
        assert not (ts1 <= ts2) and not (ts2 <= ts1)


@given(time_span(unbounds='future'))
def test_outside_date(ts):
    from datetime import timedelta
    assert ts.start_date
    outsider = ts.start_date - timedelta(1)
    assert outsider not in ts


@given(time_span())
def test_empty_timespan(ts):
    assert ts >= EmptyTimeSpan <= ts, 'Empty is a subset of any TS'

    assert EmptyTimeSpan <= EmptyTimeSpan >= EmptyTimeSpan, \
        'Empty is a subset of itself'

    assert not EmptyTimeSpan, 'Empty is considered False'

    assert not (ts <= EmptyTimeSpan), 'Empty is not a superset of any TS'

    with pytest.raises(TypeError):
        type(EmptyTimeSpan)()

    assert EmptyTimeSpan & ts == EmptyTimeSpan * ts == EmptyTimeSpan
    assert EmptyTimeSpan | ts == EmptyTimeSpan + ts == ts


@given(time_span(unbounds='none'), time_span())
def test_failure_of_triple_intersection(ts1, ts2):
    from datetime import timedelta
    ts0 = TimeSpan.from_date(ts1.start_date - timedelta(1))
    assert not (ts0 & ts1 & ts2)


@given(strategies.dates())
def test_xoutil_dates_are_representable(value):
    from xoutil.future.datetime import date
    class mydate(date):
        pass
    value = mydate(value.year, value.month, value.day)
    assert value.strftime('%Y-%m-%d')


@given(time_span('none'))
def test_timespans_are_representable(value):
    assert repr(value)


@given(time_span('none'))
def test_generate_valid_timespans(ts):
    assert ts.valid
