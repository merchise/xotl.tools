#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.aop
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
# Created on Mar 23, 2012

'''
Very simple AOP implementation allowing method replacing in objects with push
function, recover the last state with pop, reset an object to its original state
and user a special super function inner new functions used to inject the new
behavior.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

__docstring_format__ = 'rst'
__author__ = 'Medardo Rodriguez'



def change_method(obj, new_function, name=None):
    '''
    Inject the new function as replacement of existing method.
    Only for heap types, use wrapper in case you need for this same purpose.
    '''
    if not name:
        name = new_function.__name__
    cls = obj.__class__
    extended_class = type(cls.__name__, (cls,), {b'__module__': b'merchise-buildin'})
    extended_class._merchise_extended = True
    setattr(extended_class, name, new_function)
    obj.__class__ = extended_class
    return getattr(super(extended_class, obj), name, None)



def reset_methods(obj):
    '''
    Remove all extension methods from an object.
    '''
    cls = obj.__class__
    res = 0
    while cls.__dict__.get('_merchise_extended'):
        cls = cls.__base__
        res += 1
    if res > 0:
        obj.__class__ = cls
    return res



# ============ Tests =======================

class Foobar(object):
    def test(self, arg):
        print('=== %s' % self.calc(arg))

    def calc(self, arg):
        return 'Foobar: %s' % arg


class FoobarX(Foobar):
    def calc(self, arg):
        return 'FoobarX: %s' % arg


def wrap_test(obj, ctx):
    _super = None
    def test(self, arg):
        if _super:
            _super(arg)
        print('Test wrapped with:', ctx)
    _super = extend_method(obj, test)


def wrap_calc(obj, ctx):
    _super = None
    def inner(self, arg):
        return '(%s:%s)' % (_super(arg) if _super else '-', ctx)
    _super = extend_method(obj, inner, name='calc')
