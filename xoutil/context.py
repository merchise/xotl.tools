# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.context
#----------------------------------------------------------------------
# Copyright (c) 2011 Merchise Autrement
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
#
# Created on Mar 9, 2011


'''
A context manager for execution context flags.

Use as:

    >>> from xoutil import context
    >>> with context('somename'):
    ...     if context['somename']:
    ...         print('In context somename')
    In context somename
    
Note the difference creating the context and checking it.
'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

from threading import local



class LocalData(local):
    def __init__(self):
        super(LocalData, self).__init__()
        self.contexts = {}

_data = LocalData()



class MetaContext(type):
    def __getitem__(self, name):
        return _data.contexts.get(name, _null_context)



class Context(object):
    __metaclass__ = MetaContext

    def __new__(cls, name, **data):
        res = cls[name]
        if res is _null_context:
            res = super(Context, cls).__new__(cls)
            res.name = name
            res.data = data
            res.count = 0
        elif data:
            res.data.update(data)
        return res

    def __nonzero__(self):
        return self.count

    def __enter__(self):
        if self.count == 0:
            _data.contexts[self.name] = self
        self.count += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.count -= 1
        if self.count == 0:
            del _data.contexts[self.name]
        return False

# A simple alias for Context
context = Context


class NullContext(object):
    '''
    Singleton context to be used (returned) as default when no one is defined.
    '''

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(NullContext, cls).__new__(cls)
        return cls.instance

    def __nonzero__(self):
        return False

    def __enter__(self):
        from xoutil.types import Unset
        return Unset

    def __exit__(self, exc_type, exc_value, traceback):
        return False



_null_context = NullContext()


class SimpleClose(object):
    '''
    A very simple close manager that just call the argument function exiting the
    manager.
    '''
    def __init__(self, close_funct, *args, **kwargs):
        self.close_funct = close_funct
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_funct(*self.args, **self.kwargs)
        return False

