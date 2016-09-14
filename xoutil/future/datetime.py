#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.future.datetime
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
# DJango and generalized.
#
# Created on 2012-02-15

'''Extends the standard `datetime` module.

- Python's `datetime.datetime.strftime`:meth: doesn't handle dates previous to
  1900.  This module define classes to override `date` and `datetime` to
  support the formatting of a date through its full proleptic Gregorian date
  range.

Based on code submitted to comp.lang.python by Andrew Dalke, copied from
Django and generalized.

You may use this module as a drop-in replacement of the standard library
`datetime`:mod: module.

`date`:class: and `datetime`:class: classes are redefined if `strftime` method
goes wrong with some dates; `ORG` contains original definitions.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

from datetime import *    # noqa

# TODO: Consider use IoC to extend python datetime module


class WEEKDAY:
    'Simple constants for ".weekday()" method'
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class ISOWEEKDAY:
    'Simple constants for ".weekday()" method'
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class ORG:
    'Original definitions for `date` and `datetime` classes.'
    date = date
    datetime = datetime


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


def _year_find_all(fmt, year, no_year_tuple):
    import re
    import time
    text = time.strftime(fmt, (year,) + no_year_tuple)
    regex = re.compile(str(year))
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


# This library does not support strftime's "%s" or "%y" format strings.
# Allowed if there's an even number of "%"s because they are escaped.
import re    # noqa
_illegal_formatting = re.compile(br"((^|[^%])(%%)*%[sy])")
del re


def strftime(dt, fmt):
    '''Used in `strftime` method of `date` and `datetime` redefined classes.

    Also could be used with standard instances.

    '''
    import time
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
            res = time.strftime(fmt, (year,) + no_year_tuple)
            syear = "%04d" % dt.year
            for site in sites:
                res = res[:site] + syear + res[site + 4:]
            return res
        else:
            msg = 'strftime of dates before 1900 does not handle  %s'
            raise TypeError(msg % illegal_formatting.group(0))


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


# daterange([start,] stop[, step])
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

try:
    timezone
except NameError:
    # Copied from Python 3.5.2
    # TODO: Document this in xoutil

    class timezone(tzinfo):
        '''Fixed offset from UTC implementation of tzinfo.'''

        __slots__ = '_offset', '_name'

        # Sentinel value to disallow None
        _Omitted = object()

        def __new__(cls, offset, name=_Omitted):
            if not isinstance(offset, timedelta):
                raise TypeError("offset must be a timedelta")
            if name is cls._Omitted:
                if not offset:
                    return cls.utc
                name = None
            elif not isinstance(name, str):
                raise TypeError("name must be a string")
            if not cls._minoffset <= offset <= cls._maxoffset:
                raise ValueError("offset must be a timedelta "
                                 "strictly between -timedelta(hours=24) and "
                                 "timedelta(hours=24).")
            if (offset.microseconds != 0 or offset.seconds % 60 != 0):
                raise ValueError("offset must be a timedelta "
                                 "representing a whole number of minutes")
            return cls._create(offset, name)

        @classmethod
        def _create(cls, offset, name=None):
            self = tzinfo.__new__(cls)
            self._offset = offset
            self._name = name
            return self

        def __getinitargs__(self):
            """pickle support"""
            if self._name is None:
                return (self._offset,)
            return (self._offset, self._name)

        def __eq__(self, other):
            if type(other) != timezone:
                return False
            return self._offset == other._offset

        def __hash__(self):
            return hash(self._offset)

        def __repr__(self):
            """Convert to formal string, for repr().

            >>> tz = timezone.utc
            >>> repr(tz)
            'datetime.timezone.utc'
            >>> tz = timezone(timedelta(hours=-5), 'EST')
            >>> repr(tz)
            "datetime.timezone(datetime.timedelta(-1, 68400), 'EST')"
            """
            if self is self.utc:
                return 'datetime.timezone.utc'
            try:
                qn = self.__class__.__qualname__    # not valid in Python 2
            except AttributeError:
                qn = self.__class__.__name__
            if self._name is None:
                return "%s.%s(%r)" % (self.__class__.__module__, qn,
                                      self._offset)
            else:
                return "%s.%s(%r, %r)" % (self.__class__.__module__, qn,
                                          self._offset, self._name)

        def __str__(self):
            return self.tzname(None)

        def utcoffset(self, dt):
            if isinstance(dt, datetime) or dt is None:
                return self._offset
            raise TypeError("utcoffset() argument must be a datetime instance"
                            " or None")

        def tzname(self, dt):
            if isinstance(dt, datetime) or dt is None:
                if self._name is None:
                    return self._name_from_offset(self._offset)
                return self._name
            raise TypeError("tzname() argument must be a datetime instance"
                            " or None")

        def dst(self, dt):
            if isinstance(dt, datetime) or dt is None:
                return None
            raise TypeError("dst() argument must be a datetime instance"
                            " or None")

        def fromutc(self, dt):
            if isinstance(dt, datetime):
                if dt.tzinfo is not self:
                    raise ValueError("fromutc: dt.tzinfo "
                                     "is not self")
                return dt + self._offset
            raise TypeError("fromutc() argument must be a datetime instance"
                            " or None")

        _maxoffset = timedelta(hours=23, minutes=59)
        _minoffset = -_maxoffset

        @staticmethod
        def _name_from_offset(delta):
            if delta < timedelta(0):
                sign = '-'
                delta = -delta
            else:
                sign = '+'
            hours, rest = divmod(delta, timedelta(hours=1))
            minutes = rest // timedelta(minutes=1)
            return 'UTC{}{:02d}:{:02d}'.format(sign, hours, minutes)

    timezone.utc = timezone._create(timedelta(0))
    timezone.min = timezone._create(timezone._minoffset)
    timezone.max = timezone._create(timezone._maxoffset)
    # _EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


# TODO: this function was intended for a local 'strftime' that it's already
# implemented in 'xoutil.future.datetime'.
if 'eight' in __name__:
    def _wrap_strftime(object, format, timetuple):
        '''Correctly substitute for %z and %Z escapes in strftime formats.'''
        # from datetime import timedelta
        import time as _time
        # Don't call utcoffset() or tzname() unless actually needed.
        freplace = None    # the string to use for %f
        zreplace = None    # the string to use for %z
        Zreplace = None    # the string to use for %Z

        # Scan format for %z and %Z escapes, replacing as needed.
        newformat = []
        push = newformat.append
        i, n = 0, len(format)
        while i < n:
            ch = format[i]
            i += 1
            if ch == '%':
                if i < n:
                    ch = format[i]
                    i += 1
                    if ch == 'f':
                        if freplace is None:
                            freplace = '%06d' % getattr(object,
                                                        'microsecond', 0)
                        newformat.append(freplace)
                    elif ch == 'z':
                        if zreplace is None:
                            zreplace = ""
                            if hasattr(object, "utcoffset"):
                                offset = object.utcoffset()
                                if offset is not None:
                                    sign = '+'
                                    if offset.days < 0:
                                        offset = -offset
                                        sign = '-'
                                    h, m = divmod(offset, timedelta(hours=1))
                                    # not a whole minute
                                    assert not m % timedelta(minutes=1)
                                    m //= timedelta(minutes=1)
                                    zreplace = '%c%02d%02d' % (sign, h, m)
                        assert '%' not in zreplace
                        newformat.append(zreplace)
                    elif ch == 'Z':
                        if Zreplace is None:
                            Zreplace = ""
                            if hasattr(object, "tzname"):
                                s = object.tzname()
                                if s is not None:
                                    # strftime is going to have at this:
                                    # escape %
                                    Zreplace = s.replace('%', '%%')
                        newformat.append(Zreplace)
                    else:
                        push('%')
                        push(ch)
                else:
                    push('%')
            else:
                push(ch)
        newformat = "".join(newformat)
        print(newformat, timetuple)
        return _time.strftime(newformat, timetuple)


    # def strftime(self, fmt):    # Method for class date
    #     "Format using strftime()."
    #     return _wrap_strftime(self, fmt, self.timetuple())


if not __name__.startswith('xoutil.future'):
    from warnings import warn
    msg = '"{}" is now deprecated and it will be removed. Use "{}" instead.'
    old_name = 'xoutil.future.{}'.format(__name__.split('.')[-1])
    warn(msg.format(__name__, old_name), stacklevel=2)
    del warn, msg, old_name
