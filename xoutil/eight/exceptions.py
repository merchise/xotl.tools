#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight.exceptions
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-10-14

'''Compatibility for exceptions between Python 2 and 3.

Python 2 defines an module named `exceptions` but Python 3 doesn't.  We
decided not to implement something similar, for example, in
`xoutil.future`:mod: package because all these exception classes are
built-ins in both Python major versions.

There are some exception classes defined in Python 2 but not in Python 3, to
keep compatibility we do some adjusts here with `BaseException`:class: and
`StandardError`:class: classes.

In Python 2, the syntax for ``raise`` statement could include at most 3
arguments; that syntax was completelly changed in Python 3:
`~BaseException.with_traceback`:meth: method will be needed to specify a
trace-back.  Unfortunately, attributes can't be set to built-in/extension
types, as `BaseException`:class: class.  So, we create a function
(`throw`:func:) you can use to replace `~BaseException.with_traceback`:meth:,
so ``raise error.with_traceback(tb)`` in Python 3, will be the same as
``throw(error, tb)`` in both versions.

In the next example, is raised a 'division by zero' but as it would be
occurred in the 'TypeError' line::

    >>> import sys
    >>> from xoutil.eight.exceptions import throw
    >>> try:
    ...     raise TypeError('xxx')
    ... except:
    ...     tb = sys.exc_info()[2]
    ...     try:
    ...         1/0
    ...     except Exception as error:
    ...         throw(error, tb)

This "bizarre" example is equivalent -in Python 3- to::

    >>> import sys
    >>> from xoutil.eight.exceptions import throw
    >>> try:
    ...     raise TypeError('xxx')
    ... except:
    ...     tb = sys.exc_info()[2]
    ...     try:
    ...         1/0
    ...     except Exception as error:
    ...         raise error.with_traceback(tb)

In Python 3 there is a new syntax (``raise error [from cause]``) no covered in
this module yet.  This will be subject for future development.

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
    with_traceback = BaseException.with_traceback    # only in Python 3
except AttributeError:
    from ._past2 import throw

    def with_traceback(self, tb):
        '''set self.__traceback__ to tb and return self.'''
        self.__traceback__ = tb
        return self
else:
    def throw(self, tb=None):
        '''Syntax unify with Python 3 for ``raise error.with_traceback(tb)``.

        Instead of use the Python `raise` statement, use ``throw(error, tb)``.

        '''
        if not tb:
            # realize if a previous `with_traceback` was called.
            tb = getattr(self, '__traceback__', None)
        raise self.with_traceback(tb) if tb else self
