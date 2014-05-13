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


def otherfunction():
    return 1
