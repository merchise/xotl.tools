#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from xotl.tools.modules import moduleproperty
from xotl.tools.objects import memoized_property


@moduleproperty
def this(self):
    return self


@moduleproperty
def store(self):
    return getattr(self, "_store", None)


@store.setter
def store(self, value):
    setattr(self, "_store", value)


@store.deleter
def store(self):
    delattr(self, "_store")


def prop(self):
    return getattr(self, "_prop", None)


def _prop_set(self, val):
    setattr(self, "_prop", val)


def _prop_del(self):
    delattr(self, "_prop")


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
    raise AssertionError("module-level memoized_property should be read-only")
