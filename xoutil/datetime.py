#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.datetime
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
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

# TODO: Consider use IoC to extend python datetime module


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from datetime import *    # noqa
from xoutil.deprecation import deprecated

from re import compile as _regex_compile
from time import strftime as _time_strftime


#: Simple constants for .weekday() method
class WEEKDAY:
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class ISOWEEKDAY:
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


try:
    date(1800, 1, 1).strftime("%Y")
except ValueError:
    # This happens in Pytnon 2.7, I was considering to replace `strftime`
    # function from `time` module, that is used for all `strftime` methods;
    # but (WTF), Python double checks the year (in each method and then again
    # in `time.strftime` function).

    class date(date):
        __doc__ = date.__doc__

        def strftime(self, fmt):
            return strftime(self, fmt)

        def __sub__(self, other):
            return assure(super(date, self).__sub__(other))

    class datetime(datetime):
        __doc__ = datetime.__doc__

        def strftime(self, fmt):
            return strftime(self, fmt)

        def __sub__(self, other):
            return assure(super(datetime, self).__sub__(other))

        def combine(self, date, time):
            return assure(super(datetime, self).combine(date, time))

        def date(self):
            return assure(super(datetime, self).date())

        @staticmethod
        def now(tz=None):
            return assure(super(datetime, datetime).now(tz=tz))

    def assure(obj):
        '''Make sure that a `date` or `datetime` instance is a safe version.

        With safe it's meant that will use the adapted subclass on this module
        or the standard if these weren't generated.

        Classes that could be assured are: `date`, `datetime`, `time` and
        `timedelta`.

        '''
        t = type(obj)
        name = t.__name__
        if name == date.__name__:
            return obj if t is date else date(*obj.timetuple()[:3])
        elif name == datetime.__name__:
            if t is datetime:
                return obj
            else:
                args = obj.timetuple()[:6] + (obj.microsecond, obj.tzinfo)
                return datetime(*args)
        elif isinstance(obj, (time, timedelta)):
            return obj
        else:
            raise TypeError('Not valid type for datetime assuring: %s' % name)
else:
    def assure(obj):
        '''Make sure that a `date` or `datetime` instance is a safe version.

        This is only a type checker alternative to standard library.

        '''
        if isinstance(obj, (date, datetime, time, timedelta)):
            return obj
        else:
            raise TypeError('Not valid type for datetime assuring: %s' % name)


@deprecated(assure)
def new_date(d):
    '''Generate a safe date from a legacy datetime date object.'''
    return date(d.year, d.month, d.day)


@deprecated(assure)
def new_datetime(d):
    '''Generate a safe "datetime" from a "datetime.date" or "datetime.datetime"
    object.

    '''
    args = [d.year, d.month, d.day]
    if isinstance(d, datetime.__base__):    # legacy datetime
        args.extend([d.hour, d.minute, d.second, d.microsecond, d.tzinfo])
    return datetime(*args)


# This library does not support strftime's "%s" or "%y" format strings.
# Allowed if there's an even number of "%"s because they are escaped.
_illegal_formatting = _regex_compile(br"((^|[^%])(%%)*%[sy])")


def _year_find_all(fmt, year, no_year_tuple):
    text = _time_strftime(fmt, (year,) + no_year_tuple)
    regex = _regex_compile(str(year))
    return {match.start() for match in regex.finditer(text)}


_TD_LABELS = 'dhms'    # days, hours, minutes, seconds


def strfdelta(delta):
    '''
    Format a timedelta using a smart pretty algorithm.

    Only two levels of values will be printed.

    ::

        >>> def t(h, m):
        ...     return timedelta(hours=h, minutes=m)

        >>> strfdelta(t(4, 56)) == '4h 56m'
        True

    '''
    from xoutil.string import strfnumber
    ss, sss = str('%s%s'), str(' %s%s')
    if delta.days:
        days = delta.days
        delta -= timedelta(days=days)
        hours = delta.total_seconds() / 60 / 60
        res = ss % (days, _TD_LABELS[0])
        if hours >= 0.01:
            res += sss % (strfnumber(hours), _TD_LABELS[1])
    else:
        seconds = delta.total_seconds()
        if seconds > 60:
            minutes = seconds / 60
            if minutes > 60:
                hours = int(minutes / 60)
                minutes -= hours * 60
                res = ss % (hours, _TD_LABELS[1])
                if minutes >= 0.01:
                    res += sss % (strfnumber(minutes), _TD_LABELS[2])
            else:
                minutes = int(minutes)
                seconds -= 60 * minutes
                res = ss % (minutes, _TD_LABELS[2])
                if seconds >= 0.01:
                    res += sss % (strfnumber(seconds), _TD_LABELS[3])
        else:
            res = ss % (strfnumber(seconds, '%0.3f'), _TD_LABELS[3])
    return res


def strftime(dt, fmt):
    if dt.year >= 1900:
        return super(type(dt), dt).strftime(fmt)
    else:
        illegal_formatting = _illegal_formatting.search(fmt)
        if illegal_formatting is None:
            year = dt.year
            # For every non-leap year century, advance by 6 years to get into
            # the 28-year repeat cycle
            delta = 2000 - year
            year += 6 * (delta // 100 + delta // 400)
            year += ((2000 - year) // 28) * 28   # Move to around the year 2000
            no_year_tuple = dt.timetuple()[1:]
            sites = _year_find_all(fmt, year, no_year_tuple)
            sites &= _year_find_all(fmt, year + 28, no_year_tuple)
            res = _time_strftime(fmt, (year,) + no_year_tuple)
            syear = "%04d" % dt.year
            for site in sites:
                res = res[:site] + syear + res[site + 4:]
            return res
        else:
            msg = ('strftime of dates before 1900 does not handle'
                   ' %s') % illegal_formatting.group(0)
            raise TypeError(msg)


def parse_date(value=None):
    if value:
        y, m, d = value.split('-')
        return date(int(y), int(m), int(d))
    else:
        return date.today()


def get_month_first(ref=None):
    '''Given a reference date, returns the first date of the same month. If
    `ref` is not given, then uses current date as the reference.
    '''
    aux = ref or date.today()
    y, m = aux.year, aux.month
    return date(y, m, 1)


def get_month_last(ref=None):
    '''Given a reference date, returns the last date of the same month. If
    `ref` is not given, then uses current date as the reference.
    '''
    aux = ref or date.today()
    y, m = aux.year, aux.month
    if m == 12:
        m = 1
        y += 1
    else:
        m += 1
    return date(y, m, 1) - timedelta(1)


def is_full_month(start, end):
    '''Returns true if the arguments comprises a whole month.
    '''
    sd, sm, sy = start.day, start.month, start.year
    em, ey = end.month, end.year
    return ((sd == 1) and (sm == em) and (sy == ey) and
            (em != (end + timedelta(1)).month))


class flextime(timedelta):
    @classmethod
    def parse_simple_timeformat(cls, which):
        if 'h' in which:
            hour, rest = which.split('h')
        else:
            hour, rest = 0, which
        return int(hour), int(rest), 0

    def __new__(cls, *args, **kwargs):
        first = None
        if args:
            first, rest = args[0], args[1:]
        _super = super(flextime, cls).__new__
        if first and not rest and not kwargs:
            hour, minutes, seconds = cls.parse_simple_timeformat(first)
            return _super(cls, hours=hour, minutes=minutes, seconds=seconds)
        else:
            return _super(cls, *args, **kwargs)


def daterange(*args):
    '''Returns an iterator that yields each date in the range of ``[start,
    stop)``, not including the stop.

    If `start` is given, it must be a date (or `datetime`) value; and in this
    case only `stop` may be an integer meaning the numbers of days to look
    ahead (or back if `stop` is negative).

    If only `stop` is given, `start` will be the first day of stop's month.

    `step`, if given, should be a non-zero integer meaning the numbers of days
    to jump from one date to the next. It defaults to ``1``. If it's positive
    then `stop` should happen after `start`, otherwise no dates will be
    yielded. If it's negative `stop` should be before `start`.

    As with `range`, `stop` is never included in the yielded dates.

    '''
    import operator
    # Use base classes to allow broader argument values
    from datetime import date, datetime
    if len(args) == 1:
        start, stop, step = None, args[0], None
    elif len(args) == 2:
        start, stop = args
        step = None
    else:
        start, stop, step = args
    if not step and step is not None:
        raise ValueError('Invalid step value %r' % step)
    if not start:
        if not isinstance(stop, (date, datetime)):
            raise TypeError('stop must a date if start is None')
        else:
            start = get_month_first(stop)
    else:
        if stop is not None and not isinstance(stop, (date, datetime)):
            stop = start + timedelta(days=stop)
    if step is None or step > 0:
        compare = operator.lt
    else:
        compare = operator.gt
    step = timedelta(days=(step if step else 1))

    # Encloses the generator so that signature validation exceptions happen
    # without needing to call next().
    def _generator():
        current = start
        while stop is None or compare(current, stop):
            yield current
            current += step
    return _generator()
