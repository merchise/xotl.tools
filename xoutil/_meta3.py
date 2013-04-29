#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil._meta3
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-04-29

'''Implements the meta() function using the Py3k syntax.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from xoutil.compat import py3k
assert py3k, 'This module should be loaded in Py3k only'

__author__ = "Manuel Vázquez Acosta <mva.led@gmail.com>"
__date__   = "Mon Apr 29 15:34:11 2013"


def metaclass(meta):
    class inner_meta(meta):
        pass

    class base(object, metaclass=inner_meta):
        pass

    old_new = meta.__new__

    @staticmethod
    def __new__(cls, name, bases, attrs):
        print('='*10, cls, '::', name, '::', bases, '::', attrs)
        bases = tuple(b for b in bases if b is not base)
        if not bases:
            bases = (object,)
        res = old_new(meta, name, bases, attrs)
        meta.__new__ = staticmethod(old_new)
        return res

    meta.__new__ = __new__

    return base


def test_meta():
    class Meta(type):
        pass

    class Base(metaclass(Meta)):
        pass

    class Entity(Base):
        pass

    assert type(Base) is Meta
    assert type(Entity) is Meta
    assert Entity.__base__ is Base
    assert Base.__base__ is object
