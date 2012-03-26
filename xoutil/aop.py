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
Very simple AOP implementation allowing method replacing in objects with change
function, reset an object to its original state and user a special super
function inner new functions used to inject the new behavior.

Aspect-oriented programming (AOP) increase modularity by allowing the separation
of cross-cutting concerns.

An aspect can alter the behavior of the base code (the non-aspect part of a
program) by applying advice (additional behavior) at various join-points (points
in a program) specified in a quantification or query called a point-cut (that 
detects whether a given join point matches).

An aspect can also make structural changes to other classes, like adding members
or parents.
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

    Uper method can be captured after this by executing::
        _super = super(obj.__class__, obj).<<method-name>>

    Returns created extended class.
    '''
    if not name:
        name = new_function.__name__
    cls = obj.__class__
    extended_class = type(cls.__name__, (cls,), {b'__module__': b'merchise-buildin'})
    extended_class._merchise_extended = True
    setattr(extended_class, name, new_function)
    obj.__class__ = extended_class
    return extended_class



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



def wrapper(inner):
    class MetaWrapper(type):
        @staticmethod
        def __getattr__(name):
            return getattr(inner.__class__, name)
        
    class Wrapper(object):
        __metaclass__ = MetaWrapper

        @staticmethod
        def __getattr__(name):
            return getattr(inner, name)

    res = Wrapper()
    
    for attr in dir(inner.__class__):
        value = getattr(inner.__class__, attr)
        if attr.startswith('__') and callable(value) and not isinstance(value, type):
            def create_method(value):
                def call(*args, **kwargs):
                    if len(args) > 0:
                        if args[0] is res:
                            args = (inner,) + args[1:]
                        if args[0] is Wrapper:
                            args = (inner.__class__,) + args[1:]
                    return value(*args, **kwargs)
                return call
            setattr(Wrapper, attr, create_method(value))

    return res



# ============ Tests =======================

class Foobar(object):
    def test(self, arg):
        print('=== %s' % self.calc(arg))

    def calc(self, arg):
        return 'Foobar: %s' % arg

    @staticmethod
    def stest(arg):
        print('Static:', arg)

    @classmethod
    def ctest(cls, arg):
        print('Class:', cls, arg)


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
