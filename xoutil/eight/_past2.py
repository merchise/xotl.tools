#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight._past2
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-12-06

'''Ancient Python 2 tools that don't function any more in Python 3.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from . import _py3
assert not _py3, 'This module should not be loaded in Py3k'


# ---- exceptions ----

def throw(self, tb=None):
    '''Syntax unify with Python 3 for ``raise error.with_traceback(tb)``.

    Instead of use the Python `raise` statement, use ``throw(error, tb)``.

    '''

    if not tb:
        # realize if a previous `with_traceback` was called.
        tb = getattr(self, '__traceback__', None)
    if tb:
        raise self, None, tb
    else:
        raise self
