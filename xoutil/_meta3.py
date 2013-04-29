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


def meta(metacls, base=object):
    class _markbase(base):
        pass

    class _meta(metacls):
        def __new__(cls, name, bases, attrs):
            bases = tuple(b for b in bases if not issubclass(b, _markbase))
            return metacls(name, bases, attrs)

    class _base(_markbase, metaclass=_meta):
        pass

    return _base


def test_meta():
    class Meta(type):
        pass

    class Base(meta(Meta)):
        pass

    class Entity(Base):
        pass

    assert type(Base) is Meta
    assert type(Entity) is Meta
    assert Entity.__base__ is Base
