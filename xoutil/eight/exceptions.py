#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight.exceptions
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
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


'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from . import _py3, exec_


try:
    from exceptions import StandardError
except ImportError:
    StandardError = Exception

try:
    BaseException = BaseException
except NameError:
    BaseException = StandardError


if _py3:
    def reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value
else:
    exec_("""def reraise(tp, value, tb=None): raise tp, value, tb""")

reraise.__doc__ = '''Raise an exception with a traceback.

In Python 2.7 this is the same as::

    raise T, V, tb

In Python 3+ this is::

    raise T(V).with_traceback(tb)

.. versionadded: 1.7.1

'''

del _py3, exec_
