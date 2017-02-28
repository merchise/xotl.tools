#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight._errors
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-02-16

'''Unified syntax differences raising exceptions.

In Python 2 the syntax for ``raise`` is::

  "raise" [type ["," value ["," traceback]]]

and in Python 3::

  "raise" [error[.with_traceback(traceback)] ["from" cause]]

You can use ``throw`` as a function to raise errors with a homogeneous syntax
using two extra arguments:

- traceback: a trace-back instance to be used.

- cause: use ``from cause`` syntax in Python 3, or simply assign the
         ``__cause__`` attribute in Python 2.

Extra arguments could be either positional or keyword, with several aliases
allowed for keyword alternative:

- For 'traceback': 'tb', '__traceback__', and 'with_traceback'.

- For 'cause': '__cause__', 'from_', 'from'\ [1]_, and 'with_cause'.

The kind for positional arguments is determined by the value type.

When ``throw`` is used without an explicit trace-back, it's "forced" from
a smart context (see `force_traceback`:func:).

.. [1] This is a reserved keyword, but it's include as an alias to allow
       its use when passing arguments in a dictionary as ``**d``.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.tasking import AutoLocal

caught = AutoLocal(cause=None, traceback=None)


def catch(*args):
    '''Catch cause and trace-back for next `throw`:func: invocation.

    With no argument get the information about the most recent exception
    caught by an except clause.

    At most two arguments are allowed:

    - An instance of `~types.TracebackType`:class: to settle the next
      `throw`:func: trace-back.

    - An instance of `BaseException`:class` to settle the next `throw`:func:
      exception cause.

    '''
    import sys
    cause, tb = parse_args(args, {})
    if tb is None and cause is not None:
        tb = getattr(cause, '__traceback__', None)
    if tb is None:
        _, aux, tb = sys.exc_info()
        if cause is None:
            cause = aux
    caught.cause = cause
    caught.traceback = tb


def parse_args(args, kwds):
    # TODO: Use 'xoutil.params' module.
    from types import TracebackType
    from xoutil.iterators import pop_first
    count = len(args)
    if count < 3:
        tb = cause = None
        msg = "unexpected extra '{}' argument."
        for arg in args:
            if isinstance(arg, BaseException):
                if cause is None:
                    cause = arg
                else:
                    raise TypeError(msg.format('cause'))
            elif isinstance(arg, TracebackType):
                if tb is None:
                   tb = arg
                else:
                    raise TypeError(msg.format('traceback'))
        if tb is None:
            names = ('tb', 'traceback', '__traceback__', 'with_traceback')
            tb = pop_first(kwds, names, None)
        if cause is None:
            names = ('cause', '__cause__', 'from', 'from_')
            cause = pop_first(kwds, names, None)
        if not kwds:
            return cause, tb
        else:
            msg = 'throw() got unexpected keyword arguments {}'
            raise TypeError(msg.format(tuple(kwds)))
    else:
        msg = 'at most 2 positional arguments allowed ({} given)'
        raise TypeError(msg.format(count))


def force_traceback(error, cause):
    '''Look a trace-back in a throw context.

    Search the `__traceback__` attribute in the `error` instance, then in the
    `cause` (if present), then in the ``throw.caught`` (see `catch`:func:),
    and finally in the system information about the most recent exception
    caught by an except clause (see `sys.exc_info`:func:).

    It's a non-sense when no trace-back is found, in that case directly
    use the ``raise`` statement.

    '''
    import sys
    name = '__traceback__'
    res = getattr(error, name, None)
    if res is None and cause is not None:
        res = getattr(cause, name, None)
    if res is None:
        aux = getattr(error, '__cause__', None)
        if aux:
            res = getattr(aux, name, None)
    if res is None:
        aux = caught.cause
        if aux:
            res = getattr(aux, name, None)
            caught.cause = None
    if res is None:
        res = sys.exc_info()[2]
    if res is not None:
        return res
    else:
        raise TypeError("A traceback object can't be obtained; in these "
                        "scenarios use directly the raise statement.")
