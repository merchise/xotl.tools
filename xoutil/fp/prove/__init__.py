#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Validity proofs for data values.

There are some basic helper functions:

- `predicative`:func: wraps a function in a way that a logical false value is
  returned on failure.  If an exception is raised, it is returned wrapped as
  an special false value.  See `~xoutil.fp.option.Maybe`:class: monad for more
  information.

- `vouch`:func: wraps a function in a way that an exception is raised if
  an invalid value (logical false by default) is returned.  This is useful to
  call functions that use "special" false values to signal a failure.

- `enfold`:func: creates a decorator to convert a function to use either the
  `predicative`:func: or the `vouch`:func: protocol.

.. versionadded:: 1.8.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


def predicative(function, *args, **kwds):
    '''Call a function in a safety wrapper returning a false value if fail.

    This converts any function into a predicate.  A predicate can be thought
    as an operator or function that returns a value that is either true or
    false.

    Predicates are sometimes used to indicate set membership: on certain
    occasions it is inconvenient or impossible to describe a set by listing
    all of its elements.  Thus, a predicate ``P(x)`` will be true or false,
    depending on whether x belongs to a set.

    If the argument `function` validates its arguments, return a valid true
    value.  There are two special conditions: first, a value treated as false
    for Python conventions (for example, ``0``, or an empty string); and
    second, when an exception is raised; in both cases the predicate will
    return an instance of `~xoutil.fp.option.Maybe`:class:.

    '''
    from xoutil.symbols import boolean
    from xoutil.fp.option import Maybe, Just, Wrong
    from xoutil.params import single
    # I don't understand anymore why a single argument must be a special case,
    # maybe because the composition problem.
    is_single = single(*args, **kwds)
    try:
        res = function(*args, **kwds)
        if isinstance(res, (boolean, Maybe)):
            if isinstance(res, Just) and res.inner:
                return res.inner
            elif isinstance(res, boolean) and is_single and args[0]:
                return args
            else:
                return res
        elif res:
            return res
        else:
            return Just(res)
    except Exception as error:
        if isinstance(error, ValueError) and is_single:
            return Wrong(args[0])
        else:
            return Wrong(error)


def vouch(function, *args, **kwds):
    '''Call a function in a safety wrapper raising an exception if it fails.

    When the wrapped function fails, an exception must be raised.  A predicate
    fails when it returns a false value.  To avoid treat false values of some
    types as fails, use `Just`:class: to return that values wrapped.

    '''
    from xoutil.symbols import boolean, Invalid
    from xoutil.clipping import small
    from xoutil.eight import type_name
    from xoutil.eight.exceptions import throw
    from xoutil.fp.option import Just, Wrong
    from xoutil.params import single
    res = function(*args, **kwds)
    if isinstance(res, boolean):
        if res:
            aux = single(*args, **kwds)
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


def enfold(checker):
    '''Create a decorator to execute a function inner a safety wrapper.

    :param checker: Could be any function to enfold, but it's intended mainly
           for `predicative`:func:  or `vouch`:func: functions.

    In the following example, the semantics of this function can be seen.  The
    definition::

        >>> @enfold(predicative)
        ... def test(x):
        ...     return 1 <= x <= 10

        >>> test(5)
        5

    It is equivalent to::

        >>> def test(x):
        ...     return 1 <= x <= 10

        >>> predicative(test, 5)
        5

    In other hand::

        >>> @enfold(predicative)
        ... def test(x):
        ...     return 1 <= x <= 10

        >>> test(15)
        5

    '''
    def wrapper(func):
        def inner(*args, **kwds):
            return checker(func, *args, **kwds)

        try:
            inner.__name__ = func.__name__
            inner.__doc__ = func.__doc__
        except Exception:
            from xoutil.clipping import small
            from xoutil.eight import string
            inner.__name__ = string.force(small(func))
        return inner
    return wrapper
