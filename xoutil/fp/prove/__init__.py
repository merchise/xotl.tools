#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.fp.prove
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created 2016-08-31

'''Prove validity of values.

There are a family of basic checker functions:

- `validate`:func: raises an exception on failure, this is useful to call
  functions that use "special" false values to signal a failure.

- `affirm`:func: returns a false value on failure, this is useful to call
  functions that could raise an exception to signal a failure.

- `safe`:func: creates a decorator to convert a function to use either the
  `validate`:func: or the `affirm`:func: protocol.

.. versionadded:: 1.8.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


def validate(function, *args, **kwds):
    '''Call a `function` inner a safety wrapper raising an exception if fail.

    Fails could be signaled with special false values such as:

    - Any `~xoutil.fp.monads.option.Wrong`:class: instance; or

    - Any false value provable as instance of
      `~xoutil.symbols.boolean`:class:, that doesn't include values as ``0``,
      ``[]``, or ``None``.

    '''
    from xoutil.symbols import boolean, Invalid
    from xoutil.future.string import small
    from xoutil.eight import type_name
    from xoutil.eight.exceptions import throw
    from xoutil.fp.monads.option import Just, Wrong
    from xoutil.fp.params import singleton
    res = function(*args, **kwds)
    if isinstance(res, boolean):
        if res:
            aux = singleton(*args, **kwds)
            if aux is not Invalid:
                res = aux
        else:
            msg = '{}() validates as false'.format(small(function))
            raise TypeError(msg)
    elif isinstance(res, Wrong):
        inner = res.inner
        if isinstance(inner, BaseException):
            throw(inner)
        else:
            msg = '{}() validates as a wrong value'.format(small(function))
            if inner is not None or not isinstance(inner, boolean):
                v, t = small(inner), type_name(inner)
                msg += ' {} of type "{}"'.format(v, t)
            raise TypeError(msg)
    elif isinstance(res, Just):
        res = res.inner
    return res


def affirm(function, *args, **kwds):
    '''Call a `function` inner a safety wrapper returning false if fail.

    This converts any function in a predicate.  A predicate can be thought as
    an operator or function that returns a value that is either true or false.
    Predicates are sometimes used to indicate set membership: sometimes it is
    inconvenient or impossible to describe a set by listing all of its
    elements.  Thus, a predicate ``P(x)`` will be true or false, depending on
    whether x belongs to a set.

    If `function` validates its arguments, return a valid true value, could be
    Always returns an instance of `~xoutil.fp.monads.option.Maybe`:class: or a
    Boolean value.

    '''
    from xoutil.symbols import boolean
    from xoutil.fp.monads.option import Maybe, Just, Wrong
    try:
        res = function(*args, **kwds)
        if isinstance(res, (boolean, Maybe)):
            if isinstance(res, Just) and res.inner:
                return res.inner
            elif isinstance(res, boolean) and len(args) == 1 and not kwds and args[0]:
                return args
            return res
        elif res:
            return res
        else:
            return Just(res)
    except BaseException as error:
        if isinstance(error, ValueError) and len(args) == 1 and not kwds:
            return Wrong(args[0])
        else:
            return Wrong(error)


def safe(checker):
    '''Create a decorator to execute a function inner a safety wrapper.

    :param checker: Could be any function safe wrapper, but it's intended
           mainly for `affirm`:func: or `validate`:func:.

    In the following example, the semantics of this function can be seen.  The
    definition::

        >>> @safe(validate)
        ... def test(x):
        ...     return 1 <= x <= 10

        >>> test(5)
        5

    It is equivalent to::

        >>> def test(x):
        ...     return 1 <= x <= 10

        >>> validate(test, 5)
        5

    In other hand::

        >>> @safe(validate)
        ... def test(x):
        ...     return 1 <= x <= 10

        >>> test(15)
        5

    '''
    def wrapper(func):
        from xoutil.future.string import small, safe_str

        def inner(*args, **kwds):
            return checker(func, *args, **kwds)

        try:
            inner.__name__ = func.__name__
            inner.__doc__ = func.__doc__
        except BaseException:
            inner.__name__ = safe_str(small(func))
        return inner
    return wrapper
