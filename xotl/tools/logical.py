#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''This entire module is deprecated, use `xotl.tools.symbols` instead.'''

from xotl.tools.deprecation import deprecate_module
deprecate_module(replacement='xotl.tools.symbols')
del deprecate_module


from xotl.tools.symbols import boolean as Logical    # noqa
