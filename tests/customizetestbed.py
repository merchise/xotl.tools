#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.customizetestbed
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-01-28

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from xoutil.modules import moduleproperty
from xoutil.decorator import memoized_property


@moduleproperty
def this(self):
    return self


@moduleproperty
def store(self):
    return getattr(self, '_store', None)


@store.setter
def store(self, value):
    setattr(self, '_store', value)


@store.deleter
def store(self):
    delattr(self, '_store')

def prop(self):
    return getattr(self, '_prop', None)
def _prop_set(self, val):
    setattr(self, '_prop', val)
def _prop_del(self):
    delattr(self, '_prop')
prop = moduleproperty(prop, _prop_set, _prop_del)


def otherfunction():
    return 1


def memoized(self):
    return self
memoized = moduleproperty(memoized, base=memoized_property)

try:
    @memoized.setter
    def memoized(self, value):
        pass
except AttributeError:
    pass  # Ok
else:
    raise AssertionError('module-level memoized_property should be read-only')
