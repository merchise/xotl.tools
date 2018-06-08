#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Solve compatibility issues for exceptions handling.

Before Python 3, module `exceptions` is defined, but not anymore.  We decided
not to implement this concept in `xoutil.future`:mod: package because all
these exception classes are built-ins in both Python major versions, so use
any of them directly.

`StandardError`:class: is undefined in Python 3, we introduce some adjustments
here in base classes (`BaseException`:class: and `StandardError`:class:
classes).

This module tries to solve, as much as possible, differences between how the
`raise``, and ``try ... except`` statements are executed between Python
versions 2 and 3.

In Python 2 the syntax for ``raise`` is::

  "raise" [type ["," value ["," traceback]]]

and in Python 3::

  "raise" [error[.with_traceback(traceback)] ["from" cause]]

If you want to be completely compatible raising exceptions with trace-backs,
use the `throw`:func: function instead the ``raise`` statement::

  throw(error, traceback=traceback, [cause=cause])

Also, Python 3 is consistent by always assigning the trace-back information in
the ``__traceback__`` attribute, and the active error in the execution context
-if any- to the ``__context__`` attribute.  But in Python 2 it is a nightmare
to obtain a good solution related with these issues.  See `catch`:func:.

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


def catch(context=None):
    '''Catch error context in being raised with a trace-back and/or a cause.

    :param context: A subclass, or instance, of `BaseException`:class:.  If
           None, `Exception`:class: is assumed as default.

    Next example of Python 3 doesn't work in Python 2::

      >>> def test():
      ...     try:
      ...         try:
      ...             1/0
      ...         except Exception as error:
      ...             raise RuntimeError('xxx') from error
      ...     except Exception as error:
      ...         return error

      >>> error = test()

      >>> error.__context__ is error.__cause__
      True

      >>> isinstance(error.__cause__, ZeroDivisionError)
      True

    In this case, we can solve most issues by two replacements (``throw`` and
    ``catch``)::

      >>> def test():
      ...     try:
      ...         try:
      ...             1/0
      ...         except catch(Exception) as error:
      ...             throw(RuntimeError('xxx'), cause=error)
      ...     except catch(Exception) as error:
      ...         return error

    '''

    import sys
    if context is None:
        context = Exception
    if not _py3:
        from ._errors2 import update_context
        update_context(context)
    return context


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
        from ._errors2 import raise2
        raise2(error, traceback, cause)


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
