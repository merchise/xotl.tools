#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''This entire module is deprecated, use `xoutil.symbols` instead.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)

from xoutil.deprecation import deprecate_module
deprecate_module(replacement='xoutil.symbols')
del deprecate_module


from xoutil.symbols import boolean as Logical    # noqa
