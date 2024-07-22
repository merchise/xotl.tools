#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import calendar
import pickle

import pytest
from hypothesis import given, settings, strategies
from xotl.tools.future.datetime import (
    DateTimeSpan,
    EmptyTimeSpan,
    TimeSpan,
    date,
    daterange,
    datetime,
    get_month_first,
    get_month_last,
    get_next_friday,
    get_next_monday,
    get_next_saturday,
    get_next_sunday,
    get_next_thursday,
    get_next_tuesday,
    get_next_wednesday,
    get_previous_friday,
    get_previous_monday,
    get_previous_saturday,
    get_previous_sunday,
    get_previous_thursday,
    get_previous_tuesday,
    get_previous_wednesday,
    parse_date,
    parse_datetime,
    timedelta,
)
from xotl.tools.testing.datetime import datetimespans, timespans
from xotl.tools.testing.unit import run_module_doctest

dates = strategies.dates
maybe_date = dates() | strategies.none()
maybe_datetimes = strategies.datetimes() | strategies.none()


def test_datetime_imports():
    from xotl.tools.future import datetime
    from xotl.tools.future import datetime as dt

    assert datetime is dt

    from xotl.tools.future.datetime import TimeSpan
    from xotl.tools.future.datetime import TimeSpan as TS

    assert TS is TimeSpan


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


@given(timespans(), timespans())
def test_intersection_commutable(ts1, ts2):
    # Commutable
    assert ts2 * ts1 == (ts1 & ts2)


@given(timespans(), timespans())
def test_intersection_containment(ts1, ts2):
    overlap = ts1 * ts2
    if overlap is not None:
        # The intersection must always be totally covered by both ts1 and ts2,
        # unless ts1 and ts2 don't intersect
        assert (overlap & ts1) == overlap
        assert (overlap <= ts1) is True
        assert (overlap <= ts2) is True


@given(timespans(), timespans())
def test_comparision(ts1, ts2):
    if ts1 <= ts2 <= ts1:
        assert ts1 == ts2
    if ts1 == ts2:
        assert ts1 <= ts2 <= ts1

    # Single day intersection and equality test
    if ts1.start_date:
        assert ts1 * ts1.start_date == ts1.start_date
        assert ts1.start_date * ts1 == ts1.start_date
        assert ts1.start_date in ts1


@given(timespans(unbounds="none"), strategies.dates())
def test_containment_of_dates_in_timespan(ts, dt):
    assert (ts.start_date <= dt <= ts.end_date) == (dt in ts)
    assert (dt <= ts.end_date) == (dt in ts.replace(start_date=None))
    assert (ts.start_date <= dt) == (dt in ts.replace(end_date=None))
    assert dt in ts.replace(start_date=None, end_date=None)


@given(timespans(unbounds="none"), strategies.datetimes())
def test_containment_of_datetimes_in_timespan(ts, dt):
    d = dt.date()
    assert (ts.start_date <= d <= ts.end_date) == (dt in ts)
    assert (d <= ts.end_date) == (dt in ts.replace(start_date=None))
    assert (ts.start_date <= d) == (dt in ts.replace(end_date=None))
    assert dt in ts.replace(start_date=None, end_date=None)


@given(datetimespans(unbounds="none"), strategies.datetimes())
def test_containment_of_datetimes_in_datetimespan(ts, dt):
    assert (ts.start_datetime <= dt <= ts.end_datetime) == (dt in ts)
    assert (dt <= ts.end_datetime) == (dt in ts.replace(start_datetime=None))
    assert (ts.start_datetime <= dt) == (dt in ts.replace(end_datetime=None))
    assert dt in ts.replace(start_datetime=None, end_datetime=None)


@given(timespans() | datetimespans())
def test_containment_of_nondate_in_spans(ts):
    assert 1 not in ts


@given(timespans(), datetimespans())
@settings(deadline=500)
def test_interaction_timespan_with_datetimespans(ts, dts):
    assert isinstance(dts & ts, (DateTimeSpan, type(EmptyTimeSpan)))
    assert isinstance(ts & dts, (DateTimeSpan, type(EmptyTimeSpan)))

    assert DateTimeSpan.from_timespan(ts) == ts
    assert ts == DateTimeSpan.from_timespan(ts)

    ts = TimeSpan("2018-01-01", "2018-01-01")
    dts = DateTimeSpan("2018-01-01 00:00:01", "2018-01-01 00:00:02")

    assert ts != dts
    assert dts != ts


@given(timespans(), timespans(), dates())
def test_general_cmp_properties(ts1, ts2, date):
    assert bool(ts1 <= ts2) == bool(ts2 >= ts1)
    # In Python 2, dates have a __le__ that does no compare to timespans.
    assert bool(TimeSpan.from_date(date) <= ts2) == bool(ts2 >= date)

    overlap = ts1 & ts2
    if not overlap:
        # Disjoint sets are not orderable...
        assert not (ts1 <= ts2) and not (ts2 <= ts1)


@given(timespans(unbounds="future"))
def test_outside_date(ts):
    from datetime import timedelta

    assert ts.start_date
    outsider = ts.start_date - timedelta(1)
    assert outsider not in ts


@given(datetimespans(dates=strategies.datetimes(min_value=datetime(1, 1, 2)), unbounds="future"))
def test_outside_datetime(dts):
    from datetime import timedelta

    assert dts.start_date
    outsider = dts.start_date - timedelta(1)
    assert outsider not in dts


@given(timespans() | datetimespans())
def test_empty_timespan(ts):
    assert ts >= EmptyTimeSpan <= ts, "Empty is a subset of any TS"

    assert EmptyTimeSpan <= EmptyTimeSpan >= EmptyTimeSpan, "Empty is a subset of itself"

    assert not EmptyTimeSpan, "Empty is considered False"

    assert not (ts <= EmptyTimeSpan), "Empty is not a superset of any TS"

    type(EmptyTimeSpan)() is EmptyTimeSpan

    assert EmptyTimeSpan & ts == EmptyTimeSpan * ts == EmptyTimeSpan
    assert EmptyTimeSpan | ts == EmptyTimeSpan + ts == ts


@given(timespans(unbounds="none"), timespans())
def test_failure_of_triple_intersection(ts1, ts2):
    from datetime import timedelta

    ts0 = TimeSpan.from_date(ts1.start_date - timedelta(1))
    assert not (ts0 & ts1 & ts2)


@given(strategies.dates())
def test_dates_are_representable(value):
    from xotl.tools.future.datetime import date

    class mydate(date):
        pass

    value = mydate(value.year, value.month, value.day)
    assert value.strftime("%Y-%m-%d")


@given(timespans(unbounds="none"))
def test_timespans_are_representable(value):
    assert repr(value)


@given(timespans(unbounds="none"))
def test_generate_valid_timespans(ts):
    assert ts.valid


@given(timespans(unbounds="none"))
def test_ts_returns_dates_not_subtypes(ts):
    from datetime import date

    assert type(ts.start_date) is date
    assert type(ts.end_date) is date


@given(timespans(unbounds="none"), strategies.dates())
def test_operate_with_timespans(ts, d):
    assert ts.start_date - d is not None
    assert d - ts.start_date is not None


@given(timespans(unbounds="none"), timespans(unbounds="none"))
def test_definition_of_overlaps(ts1, ts2):
    assert ts1.overlaps(ts2) == bool(ts1 & ts2)


@given(timespans(unbounds="none"))
def test_duplication_of_timespans(ts1):
    ts2 = TimeSpan(ts1.start_date, ts1.end_date)
    assert {ts1, ts2} == {ts1}, "ts1 and ts2 are equal but different!"


@given(timespans(), strategies.integers(min_value=-1000, max_value=1000))
def test_timespans_displacement_reversed(ts1, delta):
    try:
        assert (ts1 << delta) == (ts1 >> -delta)
    except OverflowError:
        pass


@given(timespans(), strategies.integers(min_value=-1000, max_value=1000))
def test_timespans_displacement_keeps_unbounds(ts1, delta):
    try:
        assert ts1.unbound == (ts1 << delta).unbound
        assert ts1.future_unbound == (ts1 << delta).future_unbound
        assert ts1.past_unbound == (ts1 << delta).past_unbound
    except OverflowError:
        pass


@given(timespans(), strategies.integers(min_value=-1000, max_value=1000))
def test_timespans_displacement_doubled(ts1, delta):
    try:
        assert ((ts1 << delta) << delta) == (ts1 << (2 * delta))
    except OverflowError:
        pass


@given(timespans(), strategies.integers(min_value=-1000, max_value=1000))
def test_timespans_displacement_backandforth(ts1, delta):
    try:
        assert ts1 == ((ts1 << delta) >> delta) == (ts1 << 0) == (ts1 >> 0)
    except OverflowError:
        pass


@given(timespans(unbounds="none"), strategies.integers(min_value=-1000, max_value=1000))
def test_timespans_displacement_dates(ts1, delta):
    try:
        res = ts1 << delta
    except OverflowError:
        # Ignore if the date it's being displaced to non-supported date,
        # that's for the client to deal with
        pass
    else:
        assert (res.start_date - ts1.start_date).days == -delta
        assert (res.end_date - ts1.end_date).days == -delta
    try:
        res = ts1 >> delta
    except OverflowError:
        # Ignore if the date it's being displaced to non-supported date,
        # that's for the client to deal with
        pass
    else:
        assert (res.start_date - ts1.start_date).days == delta
        assert (res.end_date - ts1.end_date).days == delta


@given(
    timespans(unbounds="none") | datetimespans(unbounds="none"),
    strategies.integers(min_value=-1000, max_value=1000),
)
def test_timespans_displacement_keeps_the_len(ts1, delta):
    try:
        res = ts1 << delta
    except OverflowError:
        pass
    else:
        assert len(ts1) == len(res)


@given(timespans() | datetimespans())
def test_timespans_are_pickable(ts):
    for proto in range(1, pickle.HIGHEST_PROTOCOL + 1):
        assert ts == pickle.loads(pickle.dumps(ts, proto))


@given(strategies.datetimes(), strategies.datetimes())
def test_timespan_with_datetimes(d1, d2):
    from datetime import date as d
    from datetime import datetime as dt

    ts = TimeSpan(d1, d2)
    assert not isinstance(ts.start_date, dt)
    assert isinstance(ts.start_date, d)
    assert not isinstance(ts.end_date, dt)
    assert isinstance(ts.end_date, d)


@given(datetimespans())
def test_datetimespans_ts_fields(dts):
    if dts.start_datetime is None:
        assert dts.start_date is None
    else:
        assert dts.start_date == dts.start_datetime.date()
    if dts.end_datetime is None:
        assert dts.end_date is None
    else:
        assert dts.end_date == dts.end_datetime.date()


@given(maybe_date, datetimespans())
def test_setting_start_date(d, dts):
    dts.start_date = d
    if d is not None:
        assert dts.start_datetime.date() == d
        assert dts.start_datetime == datetime(d.year, d.month, d.day)
    else:
        assert dts.start_datetime is None


@given(maybe_date, datetimespans())
def test_setting_end_date(d, dts):
    dts.end_date = d
    if d is not None:
        assert dts.end_datetime.date() == d
        assert dts.end_datetime == datetime(d.year, d.month, d.day, 23, 59, 59)
    else:
        assert dts.end_datetime is None


@given(
    strategies.datetimes(min_value=datetime(1970, 1, 1), max_value=datetime(5000, 12, 31)),
    strategies.integers(min_value=1, max_value=200),
)
def test_timespan_diff(start_date, delta):
    days = timedelta(days=delta)
    big = TimeSpan(start_date, start_date + 3 * days)
    x, y = big.diff(big)
    assert x is EmptyTimeSpan and y is EmptyTimeSpan

    x, y = big.diff(EmptyTimeSpan)
    assert x == big and y is EmptyTimeSpan

    outsider = big >> 4 * days
    assert not big & outsider
    x, y = big.diff(outsider)
    assert x == big and y is EmptyTimeSpan
    x, y = outsider.diff(big)
    assert x == outsider and y is EmptyTimeSpan

    atstart = TimeSpan(start_date, start_date + days)
    assert atstart < big
    x, y = big.diff(atstart)
    assert x is EmptyTimeSpan
    assert y
    assert add_timespans(atstart, y) == big

    beforestart = TimeSpan(start_date - days, start_date + days)
    x, y = big.diff(beforestart)
    assert x is EmptyTimeSpan
    assert y
    assert add_timespans(beforestart & big, y) == big

    atend = TimeSpan(start_date + 2 * days, start_date + 3 * days)
    assert atend < big
    x, y = big.diff(atend)
    assert y is EmptyTimeSpan
    assert x
    assert add_timespans(x, atend) == big

    afterend = TimeSpan(start_date + 2 * days, start_date + 4 * days)
    x, y = big.diff(afterend)
    assert y is EmptyTimeSpan
    assert x
    assert add_timespans(x, big & afterend) == big

    middle = TimeSpan(start_date + days, start_date + 2 * days)
    assert middle < big
    x, y = big.diff(middle)
    assert x and y
    assert add_timespans(add_timespans(x, middle), y) == big

    bigger = TimeSpan(start_date - days, start_date + 4 * days)
    x, y = big.diff(bigger)
    assert x is EmptyTimeSpan and y is EmptyTimeSpan


@given(
    strategies.datetimes(min_value=datetime(1970, 1, 1), max_value=datetime(5000, 12, 31)),
    strategies.integers(min_value=1, max_value=10000),
)
@settings(deadline=None)
def test_datetimespan_diff(start_date, delta):
    secs = timedelta(seconds=delta)
    big = DateTimeSpan(start_date, start_date + 3 * secs)
    assert big.start_datetime == start_date
    assert big.end_datetime == start_date + 3 * secs
    x, y = big.diff(big)
    assert x is EmptyTimeSpan and y is EmptyTimeSpan

    x, y = big.diff(EmptyTimeSpan)
    assert x == big and y is EmptyTimeSpan

    outsider = big >> 4 * secs
    assert not big & outsider
    x, y = big.diff(outsider)
    assert x == big and y is EmptyTimeSpan
    x, y = outsider.diff(big)
    assert x == outsider and y is EmptyTimeSpan

    atstart = DateTimeSpan(start_date, start_date + secs)
    assert atstart < big
    x, y = big.diff(atstart)
    assert x is EmptyTimeSpan
    assert y
    assert add_dtspans(atstart, y) == big

    beforestart = DateTimeSpan(start_date - secs, start_date + secs)
    x, y = big.diff(beforestart)
    assert x is EmptyTimeSpan
    assert y
    assert add_dtspans(beforestart & big, y) == big

    atend = DateTimeSpan(start_date + 2 * secs, start_date + 3 * secs)
    assert atend < big
    x, y = big.diff(atend)
    assert y is EmptyTimeSpan
    assert x
    assert add_dtspans(x, atend) == big

    afterend = DateTimeSpan(start_date + 2 * secs, start_date + 4 * secs)
    x, y = big.diff(afterend)
    assert y is EmptyTimeSpan
    assert x
    assert add_dtspans(x, big & afterend) == big

    middle = DateTimeSpan(start_date + secs, start_date + 2 * secs)
    assert middle < big
    x, y = big.diff(middle)
    assert x and y
    assert add_dtspans(add_dtspans(x, middle), y) == big

    bigger = DateTimeSpan(start_date - secs, start_date + 4 * secs)
    x, y = big.diff(bigger)
    assert x is EmptyTimeSpan and y is EmptyTimeSpan


@given(datetimespans())
def test_datetimespan_repr(ts):
    assert eval(repr(ts)) == ts
    assert DateTimeSpan("2018-01-01") == DateTimeSpan(datetime(2018, 1, 1))


def test_empty_timespan_is_pickable():
    for proto in range(1, pickle.HIGHEST_PROTOCOL + 1):
        assert EmptyTimeSpan is pickle.loads(pickle.dumps(EmptyTimeSpan, proto))


@given(datetimespans())
def test_empty_span_invariants(ts):
    assert ts == EmptyTimeSpan or ts > EmptyTimeSpan
    assert ts == EmptyTimeSpan or EmptyTimeSpan < ts
    assert not (EmptyTimeSpan > ts)
    assert not (ts < EmptyTimeSpan)

    assert EmptyTimeSpan == EmptyTimeSpan
    assert EmptyTimeSpan != 1
    assert EmptyTimeSpan != date.today()
    assert EmptyTimeSpan != TimeSpan.from_date(date.today())


def add_timespans(x, y):
    if x.end_date == y.start_date - timedelta(1):
        return TimeSpan(x.start_date, y.end_date)
    else:
        raise ValueError


def add_dtspans(x, y):
    if x.end_datetime == y.start_datetime - timedelta(seconds=1):
        return DateTimeSpan(x.start_datetime, y.end_datetime)
    else:
        raise ValueError


def test_type_of_parse_date():
    assert isinstance(parse_date(), date)


def test_type_of_parse_datetime():
    assert isinstance(parse_datetime(), datetime)


@given(strategies.dates() | strategies.datetimes())
def test_get_month_last(ref: date):
    last = get_month_last(ref)
    assert last.year == ref.year
    assert last.month == ref.month
    first = last + timedelta(1)
    assert first.day == 1
    if last.month == 12:
        assert first.month == 1
    else:
        assert first.month == last.month + 1


@given(strategies.dates() | strategies.datetimes())
def test_get_month_first(ref: date):
    first = get_month_first(ref)
    assert first.month == ref.month
    assert first.year == ref.year
    assert first.day == 1


def _assert_next_WD(ref, result, expected_weekday):
    assert result.weekday() == expected_weekday
    if ref.weekday() == expected_weekday:
        assert result == ref + timedelta(7)
    else:
        assert result > ref
        try:
            last_week = result - timedelta(7)
        except OverflowError:
            # ignore overflow errors when we go to the "first date ever" `date(1, 1, 1)`.
            pass
        else:
            assert last_week < ref


@given(strategies.dates() | strategies.datetimes())
def test_get_next_monday(ref: date):
    _assert_next_WD(ref, get_next_monday(ref), calendar.MONDAY)


@given(strategies.dates() | strategies.datetimes())
def test_get_next_tuesday(ref: date):
    _assert_next_WD(ref, get_next_tuesday(ref), calendar.TUESDAY)


@given(strategies.dates() | strategies.datetimes())
def test_get_next_wednesday(ref: date):
    _assert_next_WD(ref, get_next_wednesday(ref), calendar.WEDNESDAY)


@given(strategies.dates() | strategies.datetimes())
def test_get_next_thursday(ref: date):
    _assert_next_WD(ref, get_next_thursday(ref), calendar.THURSDAY)


@given(strategies.dates() | strategies.datetimes())
def test_get_next_friday(ref: date):
    _assert_next_WD(ref, get_next_friday(ref), calendar.FRIDAY)


@given(strategies.dates() | strategies.datetimes())
def test_get_next_saturday(ref: date):
    _assert_next_WD(ref, get_next_saturday(ref), calendar.SATURDAY)


@given(strategies.dates() | strategies.datetimes())
def test_get_next_sunday(ref: date):
    _assert_next_WD(ref, get_next_sunday(ref), calendar.SUNDAY)


def _assert_previous_WD(ref, result, expected_weekday):
    assert result.weekday() == expected_weekday
    if ref.weekday() == expected_weekday:
        assert result == ref - timedelta(7)
    else:
        assert result < ref
        last_week = result + timedelta(7)
        assert last_week > ref


@given(strategies.dates() | strategies.datetimes())
def test_get_previous_monday(ref: date):
    _assert_previous_WD(ref, get_previous_monday(ref), calendar.MONDAY)


@given(strategies.dates() | strategies.datetimes())
def test_get_previous_tuesday(ref: date):
    _assert_previous_WD(ref, get_previous_tuesday(ref), calendar.TUESDAY)


@given(strategies.dates() | strategies.datetimes())
def test_get_previous_wednesday(ref: date):
    _assert_previous_WD(ref, get_previous_wednesday(ref), calendar.WEDNESDAY)


@given(strategies.dates() | strategies.datetimes())
def test_get_previous_thursday(ref: date):
    _assert_previous_WD(ref, get_previous_thursday(ref), calendar.THURSDAY)


@given(strategies.dates() | strategies.datetimes())
def test_get_previous_friday(ref: date):
    _assert_previous_WD(ref, get_previous_friday(ref), calendar.FRIDAY)


@given(strategies.dates() | strategies.datetimes())
def test_get_previous_saturday(ref: date):
    _assert_previous_WD(ref, get_previous_saturday(ref), calendar.SATURDAY)


@given(strategies.dates() | strategies.datetimes())
def test_get_previous_sunday(ref: date):
    _assert_previous_WD(ref, get_previous_sunday(ref), calendar.SUNDAY)


def test_doctests():
    run_module_doctest("xotl.tools.future.datetime")
