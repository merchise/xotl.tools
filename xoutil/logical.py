#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.logical
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2015-02-23

'''This entire module is deprecated, use `xoutil.symbols` instead.'''

from xoutil.symbols import boolean
from xoutil.deprecation import deprecated


@deprecated(boolean)
def Logical(*args, **kwargs):
    'This was a type, and now is deprecated, use instead `symbols.boolean`'
    return boolean(*args, **kwargs)

del deprecated
