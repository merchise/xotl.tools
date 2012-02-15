#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.datetime
#----------------------------------------------------------------------
# Copyright (c) 2012 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on Feb 15, 2012

'''
Python's "datetime strftime" doesn't handle dates previous to 1900.
This module define classes to override "date" and "datetime" to support
the formatting of a date through its full "proleptic Gregorian" date range.

Based on code submitted to comp.lang.python by Andrew Dalke, copied from
DJango and generalized.

>>> xotl.datetime.date(1850, 8, 2).strftime("%Y/%m/%d was a %A")
'1850/08/02 was a Friday'
'''

# TODO: consider use IoC to extend python datetime module


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)


from __future__ import (division as _py3_division, print_function as _py3_print, unicode_literals as _py3_unicode)

from re import compile as _regex_compile
import time
from time import strftime as _time_strftime

_legacy = __import__('datetime', fromlist=[b'date'], level=0)

# TODO: Maybe it's better to use IoD for this case
from xotl.data import smart_copy
smart_copy(_legacy , __import__(__name__, fromlist=[b'_legacy']), full=True)
del smart_copy

__docstring_format__ = 'rst'
__author__ = 'med'


if hasattr(_legacy.timedelta, 'total_seconds'):
    _NEW_TIME_DELTA = False
    timedelta = _legacy.timedelta
else:
    _NEW_TIME_DELTA = True
    class timedelta(_legacy.timedelta):
        __doc__ = _legacy.datetime.__doc__

        def total_seconds(self):
            return (self.microseconds + (self.seconds + self.days * 24 * 3600) * 10 ** 6) / 10 ** 6



class date(_legacy.date):
    __doc__ = _legacy.date.__doc__

    def strftime(self, fmt):
        return strftime(self, fmt)

    if _NEW_TIME_DELTA:
        def __sub__(self, other):
            res = super(date, self).__sub__(other)
            return timedelta(days=res.days, seconds=res.seconds, microseconds=res.microseconds)



class datetime(_legacy.datetime):
    __doc__ = _legacy.datetime.__doc__

    def strftime(self, fmt):
        return strftime(self, fmt)

    def combine(self, date, time):
        return datetime(date.year, date.month, date.day, time.hour, time.minute, time.second, time.microsecond, time.tzinfo)

    def date(self):
        return date(self.year, self.month, self.day)

    @staticmethod
    def now(tz=None):
        res = super(datetime, datetime).now(tz=tz)
        return datetime(res.year, res.month, res.day, res.hour, res.minute, res.second, res.microsecond, res.tzinfo)

    if _NEW_TIME_DELTA:
        def __sub__(self, other):
            res = super(datetime, self).__sub__(other)
            return timedelta(days=res.days, seconds=res.seconds, microseconds=res.microseconds)


# FIXME: "__instancecheck__", "__subclasscheck__", module "abc"
is_date = lambda obj: isinstance(obj, date.__base__)
is_datetime = lambda obj: isinstance(obj, datetime.__base__)
is_time = lambda obj: isinstance(obj, time)     # Time is not redefined

def new_date(d):
    "Generate a safe date from a legacy datetime date object."
    return date(d.year, d.month, d.day)


def new_datetime(d):
    '''Generate a safe "datetime" from a "datetime.date" or "datetime.datetime" object.'''
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
    res = set() # TODO: return {match.start() match in regex.finditer(text)}
    for match in regex.finditer(text):
        res.add(match.start())
    return res


_TIMEDELTA_LABELS = b'dhms'    # days, hours, minutes, seconds

def strfdelta(delta):
    '''
    Format a timedelta using a smart pretty algorithm.

    Only two levels of values will be printed.
    '''
    from xotl import strfnumber
    if delta.days:
        days = delta.days
        delta -= timedelta(days=days)
        hours = delta.total_seconds() / 60 / 60
        res = '%s%s' % (days, _TIMEDELTA_LABELS[0])
        return res if hours < 0.01 else res + (' %s%s' % (strfnumber(hours), _TIMEDELTA_LABELS[1]))
    else:
        seconds = delta.total_seconds()
        if seconds > 60:
            minutes = seconds / 60
            if minutes > 60:
                hours = int(minutes / 60)
                res = '%s%s' % (hours, _TIMEDELTA_LABELS[1])
                return res if minutes < 0.01 else res + (' %s%s' % (strfnumber(minutes), _TIMEDELTA_LABELS[2]))
            else:
                minutes = int(minutes)
                seconds -= 60 * minutes
                res = '%s%s' % (minutes, _TIMEDELTA_LABELS[2])
                return res if seconds < 0.01 else res + (' %s%s' % (strfnumber(seconds), _TIMEDELTA_LABELS[3]))
        else:
            return '%s%s' % (strfnumber(seconds, '%0.3f'), _TIMEDELTA_LABELS[3])



def strftime(dt, fmt):
    if dt.year >= 1900:
        return super(type(dt), dt).strftime(fmt)
    else:
        illegal_formatting = _illegal_formatting.search(fmt)
        if illegal_formatting is None:
            year = dt.year
            # For every non-leap year century, advance by 6 years to get into the 28-year repeat cycle
            delta = 2000 - year
            year += 6 * (delta // 100 + delta // 400)
            year += ((2000 - year) // 28) * 28    # Move to around the year 2000
            no_year_tuple = dt.timetuple()[1:]
            sites = _year_find_all(fmt, year, no_year_tuple)
            sites &= _year_find_all(fmt, year + 28, no_year_tuple)
            res = _time_strftime(fmt, (year,) + no_year_tuple)
            syear = "%04d" % dt.year
            for site in sites:
                res = res[:site] + syear + res[site + 4:]
            return res
        else:
            raise TypeError("strftime of dates before 1900 does not handle " + illegal_formatting.group(0))



def parse_date(value=None):
    if value:
        y, m, d = value.split('-')
        return date(int(y), int(m), int(d))
    else:
        return date.today()



def get_month_first(ref=None):
    aux = ref or date.today()
    y, m = aux.year, aux.month
    return date(y, m, 1)



def get_month_last(ref=None):
    aux = ref or date.today()
    y, m = aux.year, aux.month
    if m == 12:
        m = 1
        y += 1
    else:
        m += 1
    return date(y, m, 1) - timedelta(1)



def is_full_month(start, end):
    sd, sm, sy = start.day, start.month, start.year
    em, ey = end.month, end.year
    return (sd == 1) and (sm == em) and (sy == ey) and (em != (end + timedelta(1)).month)


del _legacy
