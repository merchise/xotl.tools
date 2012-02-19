# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.json
#----------------------------------------------------------------------
# Copyright (c) 2011 Merchise Autrement
# All rights reserved.
#
# Author: Medardo Rodriguez
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
# Created on Jul 1, 2011



'''
Interfaces for serializing objects.

Usage::
    from xotl.serializers import serialize, deserialize
    json = serialize("json", iterator, lambda item: {'pk': item.pk, 'name': item.name})
    items = tuple(deserialize("json", json))

To add your own serializers, use the SERIALIZATION_MODULES setting::

    SERIALIZATION_MODULES = {
        "csv" : "path.to.csv.serializer",
        "txt" : "path.to.txt.serializer",
    }

'''

# TODO: consider use IoC to extend python json module

from __future__ import (division as _py3_division, print_function as _py3_print, unicode_literals as _py3_unicode)

from decimal import Decimal as _Decimal
from xoutil.types import is_iterable
from xoutil.datetime import (is_datetime as _is_datetime,
                             new_datetime as _new_datetime,
                             is_date as _is_date,
                             new_date as __new_date,
                             is_time as _is_time)


_legacy = __import__(b'json', fromlist=[b'load'], level=0)

from xoutil.data import smart_copy as copy_attrs
copy_attrs(_legacy , __import__(__name__, fromlist=[b'_legacy']))
del copy_attrs


class JSONEncoder(_legacy.JSONEncoder):
    '''JSONEncoder subclass that knows how to encode date/time and decimal types.'''
    # TODO: [med]

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"


    def default(self, o):
        if _is_datetime(o):
            d = _new_datetime(o)
            return d.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif _is_date(o):
            d = __new_date(o)
            return d.strftime(self.DATE_FORMAT)
        elif _is_time(o):
            return o.strftime(self.TIME_FORMAT)
        elif isinstance(o, _Decimal):
            return str(o)
        elif is_iterable(o):
            return list(iter(o))
        return super(JSONEncoder, self).default(o)


def file_load(filename):
    with file(filename, 'r') as f:
        return load(f)


__all__ = tuple(_legacy.__all__) + (b'file_load',)
