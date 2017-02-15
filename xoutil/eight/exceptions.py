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

'''Solve compatibility issues for exceptions handling.

The syntax for the ``raise`` statement was changed in Python 3:

- ``with_traceback`` method will be needed to specify a trace-back; and

- ``[from cause]`` clause used for exception chaining (subject for future
  development).

In the first case, the best solution would be to assign a ``with_traceback``
method to the `BaseException`:class: in Python 2 (where is missing).
Unfortunately, attributes can't be set to built-in/extension types.

To fulfills both concepts, an external function (`throw`:func:) is created in
this module in order to replace new Python 3 ``raise`` syntax:

- ``throw(error, traceback=tb)`` ≣ ``raise error.with_traceback(tb)``,

- ``throw(error, cause=former_error)`` ≣ ``raise error from former_error``.

See the next hypothetical example::

    >>> import sys
    >>> from xoutil.eight.exceptions import throw
    >>> try:
    ...     StdError = StandardError
    ... except NameError as cause:    # raised only in Python 3
    ...     tb = sys.exc_info()[2]
    ...     try:
    ...         from xoutil.eight.exceptions import StandardError as StdError
    ...     except ImportError as error:    # old xoutil version?
    ...         throw(error, traceback=tb, cause=cause)

This example would be, using Python 3 syntax::

    >>> import sys
    >>> try:
    ...     StdError = StandardError
    ... except NameError as cause:    # raised only in Python 3
    ...     tb = sys.exc_info()[2]
    ...     try:
    ...         from xoutil.eight.exceptions import StandardError as StdError
    ...     except ImportError as error:    # old xoutil version?
    ...         raise error.with_traceback(tb) from cause

Python 2 defines a module named `exceptions` but Python 3 doesn't.  We decided
not to implement something similar, for example, in `xoutil.future`:mod:
package because all these exception classes are built-ins in both Python major
versions, so use any of them directly.  But `StandardError`:class: is not
defined in Python 3, for compatibility in base classes, use adjusts introduced
here in `BaseException`:class: and `StandardError`:class: classes.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

try:
    from exceptions import StandardError    # Not in Python 3
except ImportError:
    StandardError = Exception

try:
    BaseException = BaseException
except NameError:
    BaseException = StandardError


try:
    with_traceback = BaseException.with_traceback    # only in Python 3
except AttributeError:
    from ._errors2 import throw

    def with_traceback(self, tb):
        '''set self.__traceback__ to tb and return self.'''
        self.__traceback__ = tb
        return self
else:
    from ._errors3 import throw
