#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''This module simply serves the purposes of the testing weaving modules'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.modules import moduleproperty, modulemethod


def echo(what):
    return what


@moduleproperty
def this(self):
    return self


def rien():
    return 1


@modulemethod
def method(self, *args, **kwargs):
    return self, args, kwargs


@modulemethod
def selfish(self):
    return self.selfish, selfish
