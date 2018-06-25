#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Solve compatibility issues for exceptions handling.

This module tries to solve, as much as possible, differences between how the
`raise``, and ``try ... except`` statements are executed between Python
versions 2 and 3.  See `Exception Chaining and Embedded Tracebacks
<3134>`:pep:.

First issue is that before Python 3, module `exceptions` was defined, but not
anymore.  We decided not to implement this concept in `xoutil.future`:mod:
package because all these exception classes are built-ins in both Python major
versions, so use any of them directly.  But `StandardError`:class: is
undefined in Python 3, we introduce it here.

Raising an exception it's the biggest difference between both major versions,
starting with that there is no way to achieve syntax compatibility.  In
Python 2 the syntax for ``raise`` is::

  "raise" [type ["," value ["," traceback]]]

and in Python 3::

  "raise" [error[.with_traceback(traceback)] ["from" cause]]

There are two partial solutions in this module:

- Using the function `throw`:func: function instead the ``raise`` statement::

    throw([error[, traceback=traceback[, cause=cause]]])

  This is suitable only when you need the trace-back information is fully
  tracked when you raise the exception (see below).

- Using the function `grab`:func: the context_ attributes are assigned, but
  the trace-back information is not tracked in the system call context.

    raise grab(error[, traceback=traceback[, cause=cause]])

.. _context:

Python 3 is consistent by always assigning context information in the
following scenarios:

1. If an exception is raised inside an exception handler or a finally clause:
   the previous exception is then attached as the new exception's
   ``__context__`` attribute.  This is guaranteed in Python 2 using either the
   `grab`:func: function or the `throw`:func: function.

2. Clause ``from`` is used for exception chaining, the expression must be
   another exception instance or class, which will be attached to the newly
   raised exception in the ``__cause__`` attribute.  This information is
   printed when the raised exception is not handled, but in Python 2 this
   information can be custom managed by using either `grab`:func: or
   `throw`:func: function.

3. Trace-back information is automatically attached to the attribute
   ``__traceback__`` when an exception is raised.  You can set your own
   trace-back using the ``with_traceback`` method (or in the compatibility
   function `throw`:func: using ``traceback`` argument).  This can be
   partially guaranteed in Python 2 by using the `catch`:func: function in
   some exception handler or finally clause.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.symbols import Unset

try:
    StandardError    # noqa
except NameError:
    StandardError = Exception

try:
    BaseException    # noqa
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


def _force_error(error):
    if isinstance(error, type) and issubclass(error, BaseException):
        error = error()
    return error


def grab(error, traceback=Unset, cause=Unset):
    '''Prepare an error with traceback, and context to raise it.'''
    error = _force_error(error)
    if traceback is not Unset:
        error = with_traceback(error, traceback)
    if cause is not Unset:
        error.__cause__ = _force_error(cause)
    if not _py3 and error is not None:
        from ._errors2 import _fix_context
        _fix_context(error, context=catch())
    return error


def throw(error=Unset, traceback=Unset, cause=Unset):
    '''Unify syntax for raising an error with trace-back information.

    Instead of using the Python ``raise`` statement, use ``throw``::

      "raise" [error[.with_traceback(traceback)] ["from" cause]]

    becomes::

       throw([error, [traceback=traceback, ][cause=cause]])

    If `traceback` argument is not given, it is looked up in the error.


    '''
    if error is Unset:
        if traceback is Unset and cause is Unset:
            import sys
            _, error, traceback = sys.exc_info()
        else:
            raise SyntaxError('invalid syntax')
    if error is None:
        raise RuntimeError('No active exception to re-raise')
    else:
        error = grab(error, traceback=traceback, cause=cause)
        if _py3:
            if cause is None:
                raise error
            else:
                from ._errors3 import raise3
                raise3(error)
        elif error.__traceback__ is None:
            raise error
        else:
            from ._errors2 import raise2
            raise2(error)


def catch(base=Unset):
    '''Fix ``sys.exc_info`` context in Python 2.

    :param base: A subclass of `BaseException`:class: or Unset.

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

    If base is unset, the catched system error value is returned, so never use
    this function as::

      >>> try:
      ...     1/0
      ... except catch():
      ...     pass

    '''
    if not _py3:
        import sys
        from ._errors2 import _fix_context
        _, error, traceback = sys.exc_info()
        if error is not None:
            _fix_context(error, traceback=traceback)
            if base is Unset:
                base = error
    return base


def catch_traceback(error, traceback):
    '''Catch a trace-back information in a corresponding error.'''
    if not _py3 and error is not None:
        from ._errors2 import _fix_context
        _fix_context(error, traceback=traceback)


def traceof(error):
    '''Get the trace-back information of the given `error`.

    Python 3 is consistent by always assigning the trace-back information in
    the attribute ``__traceback__``, but in Python 2 it's a "little tricky" to
    obtain a good solution, and not always, only in some contexts.

    Returns None if it could not be found.

    '''
    if not _py3:
        from ._errors2 import _catch
        _catch(error)
    return error.__traceback__
