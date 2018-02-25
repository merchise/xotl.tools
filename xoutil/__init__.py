#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Collection of disparate utilities.

`xoutil` is essentially an extension to the Python's standard library, it does
not make up a full framework, but it's very useful to be used from a
diversity of scenarios.

'''
import sys
from .modules import customize
from .deprecation import DeprecatedImportDescriptor

customize(sys.modules[__name__], custom_attrs=dict(
    Unset=DeprecatedImportDescriptor('xoutil.symbols.Unset'),
    Undefined=DeprecatedImportDescriptor('xoutil.symbols.Undefined'),
    Ignored=DeprecatedImportDescriptor('xoutil.symbols.Ignored'),
    Invalid=DeprecatedImportDescriptor('xoutil.symbols.Invalid'),
))

del customize, sys, DeprecatedImportDescriptor
