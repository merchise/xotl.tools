#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight.exceptions
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-10-14

'''Solve compatibility issues for exceptions handling.

Python 2 defines a module named `exceptions` but Python 3 doesn't.  We decided
not to implement something similar, for example, in `xoutil.future`:mod:
package because all these exception classes are built-ins in both Python major
versions, so use any of them directly; nevertheless `StandardError`:class: is
undefined in Python 3, we introduce some adjustments here in base classes
(`BaseException`:class: and `StandardError`:class: classes).

The functions `catch`:func: and `throw`:func: unify syntax differences raising
exceptions.  In Python 2 the syntax for ``raise`` is::

  "raise" [type ["," value ["," traceback]]]

and in Python 3::

  "raise" [error[.with_traceback(traceback)] ["from" cause]]

You can use `catch`:func: as a function to wrap errors going to be raised with
a homogeneous syntax using a `trace` extra argument::

    >>> divisor = 0
    >>> try:
    ...     inverted = 1/divisor
    ... except BaseException:
    ...     raise catch(ValueError('Invalid divisor.'))

If you want to be completely compatible raising exceptions with trace-backs,
use the `throw`:func: function instead the ``raise`` statement.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.tasking import AutoLocal

#: Last caught trace context, see `catch`:func:.
caught = AutoLocal(cause=None, traceback=None)

try:
    from exceptions import StandardError    # Not in Python 3
except ImportError:
    StandardError = Exception

try:
    BaseException = BaseException
except NameError:
    BaseException = StandardError


try:
    with_traceback = BaseException.with_traceback    # only in python 3
    _py3 = True
except AttributeError:
    _py3 = False

    def with_traceback(self, tb):
        '''set self.__traceback__ to `tb` and return self.'''
        from types import TracebackType
        if tb is None or isinstance(tb, TracebackType):
            self.__traceback__ = tb
            return self
        else:
            raise TypeError('__traceback__ must be a traceback or None')


def with_cause(self, cause):
    '''set self.__cause__ to `cause` and return self.'''
    if cause is None or isinstance(cause, BaseException):
        self.__cause__ = cause
        return self
    else:
        msg = '__cause__ must derive from BaseException or be None'
        raise TypeError(msg)


def catch(self):
    '''Check an error to settle trace-back information if found.

    :param self: The exception to check.

    '''
    import sys
    tb = traceof(self)
    if tb is None:
        _, cause, tb = sys.exc_info()
    else:
        cause = None
    self = with_traceback(self, tb)
    if cause is not None:
        self = with_cause(self, cause)
    return self


def grab(self=None, trace=None):
    '''Prepare an error being raised with a trace-back and/or a cause.

    :param self: The exception to be raised or None to capture the current
           trace context for future use.

    :param trace: Could be a trace-back, a cause (exception instance), or both
           in a tuple (or list) with ``(cause, traceback)``.  If None, use the
           current system exception info as the trace (see
           `sys.exc_info`:func: built-in function).

    This function create a syntax for ``raise`` statement, compatible for both
    major Python versions.

    '''
    import sys
    if trace is None:
        _, cause, traceback = sys.exc_info()
        if cause is None:
            cause, traceback = caught.cause, caught.traceback
            caught.cause, caught.traceback = None, None
        if cause is None and traceback is None:
            msg = 'catch() captured invalid exception information.'
            raise RuntimeError(msg)
    elif isinstance(trace, (tuple, list)):
        if isinstance(trace[0], BaseException):
            cause, traceback = trace
        else:
            traceback, cause = trace
    elif isinstance(trace, BaseException):
        cause = trace
        traceback = getattr(cause, '__traceback__', None)
    else:
        cause, traceback = None, trace
    if self is None:
        caught.cause, caught.traceback = cause, traceback
    else:
        self = with_traceback(self, traceback)
        self = with_cause(self, cause)
        return self



def throw(error, tb=None):
    '''Unify syntax for raising an error with trace-back information.

    Instead of using the Python ``raise`` statement, use ``throw(error, tb)``.
    If `tb` argument is not given, the trace-back information is looked up in
    the context.

    '''
    if tb is None:
        tb = traceof(error)
        if tb is None:
            error = catch(error)
            tb = error.__traceback__
    if tb is None:
        raise error
    elif _py3:
        raise error.with_traceback(tb)
    else:
        from ._throw2 import raise2
        raise2(error, tb)


def traceof(error):
    '''Get the trace-back information of the given `error`.

    Return None if not defined.

    '''
    from types import TracebackType
    try:
        res = error.__traceback__
        return res if isinstance(res, TracebackType) else None
    except AttributeError:
        return None
