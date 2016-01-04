#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight.exceptions
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-10-14

'''Compatibility exceptions between Python 2 and 3.

Python 2 defines an module named `exceptions` but Python 3 doesn't.  Also,
there are some exception classes defined in Python 2 but not in Python 3.

In Python, `with_traceback` method will be assigned to function similar that
in Python 3, the problem is to use the raise statement with this syntax.  To
accomplish with similar syntax in Python 2 or 3, use the new created
`BaseException.throw`:meth:.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

try:
    from exceptions import StandardError
except ImportError:
    StandardError = Exception

try:
    BaseException = BaseException
except NameError:
    BaseException = StandardError


try:
    with_traceback = BaseException.with_traceback
except AttributeError:
    from ._past2 import throw

    def with_traceback(self, tb):
        '''set self.__traceback__ to tb and return self.'''
        self.__traceback__ = tb
        return self
else:
    def throw(self, tb=None):
        '''Syntax unify with Python 3 for ``raise error.with_traceback(tb)``.

        Instead of use the Python `raise` statement, use ``throw(error, tb)``.

        '''
        if not tb:
            # realize if a previous `with_traceback` was called.
            tb = getattr(self, '__traceback__', None)
        raise self.with_traceback(tb) if tb else self
