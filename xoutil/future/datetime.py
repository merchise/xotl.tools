#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Extends the standard `datetime` module.

- Python's ``datetime.strftime`` doesn't handle dates previous to 1900.
  This module define classes to override `date` and `datetime` to support the
  formatting of a date through its full proleptic Gregorian date range.

Based on code submitted to comp.lang.python by Andrew Dalke, copied from
Django and generalized.

You may use this module as a drop-in replacement of the standard library
`datetime` module.

'''

from datetime import *    # noqa
from datetime import timedelta
import datetime as _stdlib    # noqa

from re import compile as _regex_compile
from time import strftime as _time_strftime

from enum import IntEnum
from xoutil.deprecation import deprecated    # noqa


class WEEKDAY(IntEnum):
    '''Simple constants for 'weekday' method.'''
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class ISOWEEKDAY(IntEnum):
    '''Simple constants for 'weekday' method.'''
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


@deprecated("plain objects")
def assure(obj):
    '''Make sure that a `date` or `datetime` instance is a safe version.

    This is only a type checker alternative to standard library.

    '''
    if isinstance(obj, (date, datetime, _stdlib.time, timedelta)):
        return obj
    else:
        raise TypeError('Not valid type for datetime assuring: %s' % obj)


@deprecated(assure)
def new_date(d):
    '''Generate a safe date from a legacy datetime date object.'''
    return date(d.year, d.month, d.day)


@deprecated(assure)
def new_datetime(d):
    '''Generate a safe datetime given a legacy date or datetime object.'''
    args = [d.year, d.month, d.day]
    if isinstance(d, datetime.__base__):    # legacy datetime
        args.extend([d.hour, d.minute, d.second, d.microsecond, d.tzinfo])
    return datetime(*args)


del deprecated


# This library does not support strftime's "%s" or "%y" format strings.
# Allowed if there's an even number of "%"s because they are escaped.
_illegal_formatting = _regex_compile(br"((^|[^%])(%%)*%[sy])")


def _year_find_all(fmt, year, no_year_tuple):
    text = _time_strftime(fmt, (year,) + no_year_tuple)
    regex = _regex_compile(str(year))
    return {match.start() for match in regex.finditer(text)}


_TD_LABELS = 'dhms'    # days, hours, minutes, seconds


def _strfnumber(number, format_spec='%0.2f'):
    '''Convert a floating point number into string using a smart way.

    Used internally in strfdelta.

    '''
    res = format_spec % number
    if '.' in res:
        res = res.rstrip('0')
        if res.endswith('.'):
            res = res[:-1]
    return res


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
    ss, sss = str('%s%s'), str(' %s%s')
    if delta.days:
        days = delta.days
        delta -= timedelta(days=days)
        hours = delta.total_seconds() / 60 / 60
        res = ss % (days, _TD_LABELS[0])
        if hours >= 0.01:
            res += sss % (_strfnumber(hours), _TD_LABELS[1])
    else:
        seconds = delta.total_seconds()
        if seconds > 60:
            minutes = seconds / 60
            if minutes > 60:
                hours = int(minutes / 60)
                minutes -= hours * 60
                res = ss % (hours, _TD_LABELS[1])
                if minutes >= 0.01:
                    res += sss % (_strfnumber(minutes), _TD_LABELS[2])
            else:
                minutes = int(minutes)
                seconds -= 60 * minutes
                res = ss % (minutes, _TD_LABELS[2])
                if seconds >= 0.01:
                    res += sss % (_strfnumber(seconds), _TD_LABELS[3])
        else:
            res = ss % (_strfnumber(seconds, '%0.3f'), _TD_LABELS[3])
    return res


def strftime(dt, fmt):
    '''Used as `strftime` method of `date` and `datetime` redefined classes.

    Also could be used with standard instances.

    '''
    if dt.year >= 1900:
        bases = type(dt).mro()
        i = 0
        base = _strftime = type(dt).strftime
        while _strftime == base:
            aux = getattr(bases[i], 'strftime', base)
            if aux != base:
                _strftime = aux
            else:
                i += 1
        return _strftime(dt, fmt)
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


def get_next_month(ref=None, lastday=False):
    '''Get the first or last day of the *next month*.

    If `lastday` is False return the first date of the `next month`.
    Otherwise, return the last date.

    The *next month* is computed with regards to a reference date.  If `ref`
    is None, take the current date as the reference.

    Examples:

      >>> get_next_month(date(2017, 1, 23))
      date(2017, 2, 1)

      >>> get_next_month(date(2017, 1, 23), lastday=True)
      date(2017, 2, 28)

    .. versionadded:: 1.7.3

    '''
    result = get_month_last(ref) + timedelta(days=1)
    if lastday:
        return get_month_last(result)
    else:
        return result


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
        _super = super().__new__
        if first and not rest and not kwargs:
            hour, minutes, seconds = cls.parse_simple_timeformat(first)
            return _super(cls, hours=hour, minutes=minutes, seconds=seconds)
        else:
            return _super(cls, *args, **kwargs)


# TODO: Merge this with the new time span.
def daterange(*args):
    '''Similar to standard 'range' function, but for date objets.

    Returns an iterator that yields each date in the range of ``[start,
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


infinity_extended_date = date


class DateField:
    '''A simple descriptor for dates.

    Ensures that assigned values must be parseable dates and parses them.

    '''
    def __init__(self, name, nullable=False):
        self.name = name
        self.nullable = nullable

    def __get__(self, instance, owner):
        from xoutil.context import context
        if instance is not None:
            res = instance.__dict__[self.name]
            if res and NEEDS_FLEX_DATE in context:
                return infinity_extended_date(res.year, res.month, res.day)
            else:
                return res
        else:
            return self

    def __set__(self, instance, value):
        from datetime import datetime as dt, date
        if value in (None, False):
            # We regard False as None, so that working with Odoo is easier:
            # missing values in Odoo, often come as False instead of None.
            if not self.nullable:
                raise ValueError('Setting None to a required field')
            else:
                value = None
        elif isinstance(value, dt):
            value = value.date()
        elif not isinstance(value, date):
            value = parse_date(value)
        instance.__dict__[self.name] = value


class TimeSpan:
    '''A *continuous* span of time.

    Time spans objects are iterable.  They yield exactly two times: first the
    start date, and then the end date::

       >>> ts = TimeSpan('2017-08-01', '2017-09-01')
       >>> tuple(ts)
       (date(2017, 8, 1), date(2017, 9, 1))

    Time spans objects have two items::

       >>> ts[0]
       date(2017, 8, 1)

       >>> ts[1]
       date(2017, 9, 1)

       >>> ts[:]
       (date(2017, 8, 1), date(2017, 9, 1))

    Two time spans are equal if their start_date and end_date are equal.  When
    comparing a time span with a date, the date is coerced to a time span
    (`from_date`:meth:).

    A time span with its `start` set to None is unbound to the past.  A time
    span with its `end` set to None is unbound to the future.  A time span
    that is both unbound to the past and the future contains all possible
    dates.  A time span that is not unbound in any direction is
    `bound <bound>`:attr:.

    A bound time span is `valid`:attr: if its start date comes before its end
    date.

    Time spans can `intersect <__mul__>`:meth:, compared for containment of
    dates and by the subset/superset order operations (``<=``, ``>=``).  In
    this regard, they represent the *set* of dates between `start` and `end`,
    inclusively.

    .. warning:: Time spans don't implement the union or difference operations
       expected in sets because the difference/union of two span is not
       necessarily *continuous*.

    '''
    start_date = DateField('start_date', nullable=True)
    end_date = DateField('end_date', nullable=True)

    def __init__(self, start_date=None, end_date=None):
        self.start_date = start_date
        self.end_date = end_date

    @classmethod
    def from_date(self, date):
        '''Return a new time span that covers a single `date`.'''
        return self(start_date=date, end_date=date)

    @property
    def past_unbound(self):
        'True if the time span is not bound into the past.'
        return self.start_date is None

    @property
    def future_unbound(self):
        'True if the time span is not bound into the future.'
        return self.end_date is None

    @property
    def unbound(self):
        '''True if the time span is `unbound into the past <past_unbound>`:attr: or
        `unbount into the future <future_unbound>`:attr: or both.

        '''
        return self.future_unbound or self.past_unbound

    @property
    def bound(self):
        'True if the time span is not `unbound <unbound>`:attr:.'
        return not self.unbound

    @property
    def valid(self):
        '''A bound time span is valid if it starts before it ends.

        Unbound time spans are always valid.

        '''
        from xoutil.context import context
        with context(NEEDS_FLEX_DATE):
            if self.bound:
                return self.start_date <= self.end_date
            else:
                return True

    def __contains__(self, other):
        '''Test if we completely cover `other` time span.

        A time span completely cover another one if every day contained by
        `other` is also contained by `self`.

        Another way to define it is that ``self & other == other``.

        '''
        from datetime import date
        if isinstance(other, date):
            if self.start_date and self.end_date:
                return self.start_date <= other <= self.end_date
            elif self.start_date:
                return self.start_date <= other
            elif self.end_date:
                return other <= self.end_date
            else:
                return True
        else:
            return False

    def overlaps(self, other):
        '''Test if the time spans overlaps.'''
        return bool(self & other)

    def isdisjoint(self, other):
        return not self.overlaps(other)

    def __le__(self, other):
        'True if `other` is a superset.'
        return (self & other) == self

    issubset = __le__

    def __lt__(self, other):
        'True if `other` is a proper superset.'
        return self != other and self <= other

    def __gt__(self, other):
        'True if `other` is a proper subset.'
        return self != other and self >= other

    def __ge__(self, other):
        'True if `other` is a subset.'
        # Notice that ge is not the opposite of lt.
        return (self & other) == other

    issuperset = covers = __ge__

    def __iter__(self):
        yield self.start_date
        yield self.end_date

    def __getitem__(self, index):
        this = tuple(self)
        return this[index]

    def __eq__(self, other):
        import datetime
        if isinstance(other, datetime.date):
            other = type(self).from_date(other)
        if not isinstance(other, TimeSpan):
            other = type(self)(other)
        return (self.start_date == other.start_date and
                self.end_date == other.end_date)

    def __hash__(self):
        return hash((self.start_date, self.end_date))

    def __ne__(self, other):
        return not (self == other)

    def __and__(self, other):
        '''Get the time span that is the intersection with another time span.

        If two time spans don't overlap, return the `empty time span
        <EmptyTimeSpan>`:obj:.

        If `other` is not a TimeSpan we try to create one.  If `other` is a
        date, we create the TimeSpan that starts and end that very day. Other
        types are passed unchanged to the constructor.

        '''
        import datetime
        from xoutil.infinity import Infinity
        from xoutil.context import context
        if isinstance(other, _EmptyTimeSpan):
            return other
        elif isinstance(other, datetime.date):
            other = TimeSpan.from_date(other)
        elif not isinstance(other, TimeSpan):
            raise TypeError("Invalid type '%s'" % type(other).__name__)
        with context(NEEDS_FLEX_DATE):
            start = max(
                self.start_date or -Infinity,
                other.start_date or -Infinity
            )
            end = min(
                self.end_date or Infinity,
                other.end_date or Infinity
            )
        if start <= end:
            if start is -Infinity:
                start = None
            if end is Infinity:
                end = None
            return type(self)(start, end)
        else:
            return EmptyTimeSpan
    __mul__ = __rmul__ = __rand__ = __and__

    def __bool__(self):
        return True

    __nonzero__ = __bool__

    def __len__(self):
        '''The amount of dates in the span.

        .. warning:: If the time span is `unbound`:attr: this method returns
                     NotImplemented.  This will make python complain with a
                     TypeError.

        .. versionadded:: 1.8.2

        '''
        if self.bound:
            return (self.end_date - self.start_date).days
        else:
            return NotImplemented

    def __lshift__(self, delta):
        '''Return the time span displaced to the past in `delta`.

        :param delta: The number of days to displace.  It can be either an
                      integer or a `datetime.timedelta`:class:.  The integer
                      will be converted to ``timedelta(days=delta)``.

        .. note:: Delta values that don't amount to at least a day will be the
                  same as 0.

        .. versionadded:: 1.8.2

        .. warning:: Python does have a boundaries for the dates it can
           represent, so displacing a TimeSpan can cause OverflowError.

        '''
        import numbers
        if isinstance(delta, numbers.Integral):
            delta = timedelta(days=delta)   # noqa
        start = self.start_date - delta if self.start_date else None
        end = self.end_date - delta if self.end_date else None
        return type(self)(start, end)

    def __rshift__(self, delta):
        '''Return the time span displaced to the future in `delta`.

        :param delta: The number of days to displace.  It can be either an
                      integer or a `datetime.timedelta`:class:.  The integer
                      will be converted to ``timedelta(days=delta)``.

        .. note:: Delta values that don't amount to at least a day will be the
                  same as 0.

        .. versionadded:: 1.8.2

        .. warning:: Python does have a boundaries for the dates it can
           represent, so displacing a TimeSpan can cause OverflowError.

        '''
        return self << -delta

    def intersection(self, *others):
        'Return ``self [& other1 & ...]``.'
        import operator
        from functools import reduce
        return reduce(operator.mul, others, self)

    def __repr__(self):
        start, end = self
        return 'TimeSpan(%r, %r)' % (start.isoformat() if start else None,
                                     end.isoformat() if end else None)


class _EmptyTimeSpan:
    __slots__ = []  # no inner structure

    def __bool__(self):
        return False

    __nonzero__ = __bool__

    def __contains__(self, which):
        return False  # I don't contain noone

    # The empty is equal only to itself
    def __eq__(self, which):
        from datetime import date
        if isinstance(which, (TimeSpan, date, _EmptyTimeSpan)):
            # We expect `self` to be a singleton, but pickle protocol 1 does
            # not warrant to call our __new__.
            return self is which
        else:
            raise TypeError

    def __ne__(self, which):
        return not (self == which)

    # The empty set is a subset of any other set.  dates are regarded as the
    # set that contains that
    def __le__(self, which):
        from datetime import date
        if isinstance(which, (TimeSpan, date, _EmptyTimeSpan)):
            return True
        else:
            raise TypeError

    # The empty set is only a superset of itself.
    __ge__ = covers = __eq__

    # The empty set is a *proper* subset of any set but itself.  The empty
    # set is disjoint with any other set but itself.
    __lt__ = isdisjoint = __ne__

    # The empty set is a *proper* superset of no one
    def __gt__(self, which):
        from datetime import date
        if isinstance(which, (TimeSpan, date, _EmptyTimeSpan)):
            return True
        else:
            raise TypeError

    # `empty | x == empty + x == x`
    def __add__(self, which):
        from datetime import date
        if isinstance(which, (TimeSpan, date, _EmptyTimeSpan)):
            return which
        else:
            raise TypeError

    __or__ = __add__

    # `empty & x == empty * x == empty`
    def __mul__(self, other):
        from datetime import date
        if isinstance(other, (TimeSpan, date, _EmptyTimeSpan)):
            return self
        else:
            raise TypeError

    __and__ = __mul__

    def __repr__(self):
        return 'EmptyTimeSpan'

    def __new__(cls):
        res = getattr(cls, '_instance', None)
        if res is None:
            res = cls._instance = super().__new__(cls)
        return res

    def __reduce__(self):
        # So that unpickling returns the singleton
        return type(self), ()

    def __len__(self):
        return 0

    def __lshift__(self, delta):
        return self

    def __rshift__(self, delta):
        return self


EmptyTimeSpan = _EmptyTimeSpan()


#: A context to switch on/off returning a subtype of date from DateFields.
#: Used within `TimeSpan` to allow comparison with `Infinity`.
NEEDS_FLEX_DATE = object()


del IntEnum
