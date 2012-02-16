# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xotl.stack
#----------------------------------------------------------------------
# Copyright (c) 2009-2011 Merchise Autrement
# All rights reserved.
#
# Author: Medardo Rodriguez
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
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


'''Utilities to inspect the CPython's stack.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

import inspect


MAX_DEEP = 15


def getargvalues(frame):
    pos, args, kwds, values = inspect.getargvalues(frame)
    res = {}
    for key in pos:
        res[key] = values[key]
    if args:
        i = 0
        for item in values[args]:
            res['%s[%s]' % (args, i)] = item
            i += 1
    if kwds:
        res.update(values[kwds])
    return res


def object_info_finder(obj_type, arg_name=None, max_deep=MAX_DEEP):
    '''
    Find an object of the given type through all arguments in stack frames.
    Returns a tuple with the following values:
    (arg-value, arg-name, deep, frame).
    When no object is found 
    None is returned.

    Arguments:
        object_type: a type or a tuple of types as in "isinstance".
        arg_name: the arg_name to find; if None find in all arguments
        max_deep: the max deep to enter in the stack frames.
    '''
    frame = inspect.currentframe()
    deep = 0
    res = None
    while (res is None) and (deep < max_deep) and (frame is not None):
        ctx = getargvalues(frame)
        d = {arg_name: ctx.get(arg_name)} if arg_name is not None else ctx
        for key, value in d.iteritems():
            if isinstance(value, obj_type):
                res = (value, key, deep, frame)
        frame = frame.f_back
        deep += 1
    return res



def object_finder(obj_type, arg_name=None, max_deep=MAX_DEEP):
    finder = object_info_finder(obj_type, arg_name, max_deep)
    info = finder()
    return info[0] if info else None



def track_value(value, max_deep=MAX_DEEP):
    '''
    Find a value through all arguments in stack frames.
    Returns a dictionary with the full-context in the same level as "value".
    '''
    frame = inspect.currentframe().f_back.f_back
    deep = 0
    res = None
    while (res is None) and (deep < max_deep) and (frame is not None):
        ctx = getargvalues(frame)
        for _key, _value in ctx.iteritems():
            if (type(value) == type(_value)) and (value == _value):
                res = (ctx, _key)
        frame = frame.f_back
        deep += 1
    return res



__all__ = (b'MAX_DEEP', b'getargvalues', b'object_info_finder',
           b'object_finder', b'track_value')

