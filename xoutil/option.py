#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.option
# ---------------------------------------------------------------------
# Copyright (c) 2015, 2016 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-12-07

'''Functional Programming *Option Type* definition.

In Programming, and Type Theory, an *option type*, or *maybe type*, represents
encapsulation of an optional value; e.g., it is used in functions which may or
may not return a meaningful value when they are applied.

It consists of either a constructor encapsulating the original value ``x``
(written ``Just x`` or ``Some x``) or an empty constructor (called *None* or
*Nothing*).  Outside of functional programming, these are known as *nullable
types*.

In our case *option type* will be the `Maybe`:class: class (the equivalent of
`Option` in *Scala Programming Language*), the wrapper for valid values will
be the `Just`:class: class (equivalent of `Some` in *Scala*); and the wrapper
for invalid values will be the `Wrong`:class: class.

Instead of *None* or *Nothing*, `Wrong` is used because two reasons:
(1) already existence of `None` special Python value, and (2) `Wrong`:class:
also wraps incorrect values and can have several instances (not only a *null*
value).

It could be thought that this kind of concept is useless in Python because
the dynamic nature of the language, but always there are certain logic systems
that need to wrap "correct" false values and "incorrect" true values.

Also, in functional programming, errors can be reasoned in a new way: more
like as *error values* than in *exception handling*.  Where the `Maybe`:class:
type expresses the failure possibility through `Wrong`:class: instances
encapsulating errors.

When receiving a `Wrong`:class: instance encapsulating an error, and want to
recover the *exception propagation style* -instead of continue in *pure
functional programming*-, to re-raise the exception, instead the `raise`
Python statement, use `~xoutil.eight.exceptions.throw`:func:.

See https://en.wikipedia.org/wiki/Monad_%28functional_programming%29\
#The_Maybe_monad

'''

# TODO: move to xaskell package

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


class Maybe(object):
    '''Wrapper for optional values.

    The Maybe type encapsulates an optional value.  A value of type ``Maybe
    a`` either contains a value of type ``a`` (represented as ``Just a``), or
    it is empty (represented as ``Nothing``).  Using `Maybe`` is a good way to
    deal with errors or exceptional cases without resorting to drastic
    measures such as error. In this implementation we make a variation where a
    ``Wrong`` object represents a missing (with special value ``Nothing``) or
    an improper value (including errors).

    See descendant classes `Just`:class: and `Wrong`:class: for more
    information.

    This implementation combines ``Maybe`` and ``Either`` Haskell data types.
    ``Maybe`` is a means of being explicit that you are not sure that a
    function will be successful when it is executed.  Conventionally, the
    usage of ``Either`` for errors uses ``Right`` when the computation is
    successful, and ``Left`` for failing scenarios.

    In this implementation, `Just`:class` us used for equivalence with both
    Haskell ``Just`` and ``Right`` types; `Wrong`:class: is used with the
    special value ``Nothing`` and to encapsulate errors or incorrect values
    (Haskell ``Left``).

    Haskell::

      data Maybe a = Nothing | Just a

      either :: (a -> c) -> (b -> c) -> Either a b -> c

    Case analysis for the Either type.  If the value is Left a, apply the
    first function to a; if it is Right b, apply the second function to b.

    '''
    __slots__ = 'inner'
    _singletons = [None, None, None]    # False, True, None

    def __new__(cls, *args):
        default = cls is Just
        if len(args) == 0:
            arg = default
        elif len(args) == 1:
            arg = args[0]
        else:
            msg = '{}: receive too many arguments "{}"'
            raise TypeError(msg.format(cls.__name__, len(args)))
        if arg is default or arg is None and cls is Wrong:
            idx = 2 if arg is None else arg
            if cls._singletons[idx] is None:
                self = super(Maybe, cls).__new__(cls)
                self.inner = arg
                cls._singletons[idx] = self
            return cls._singletons[idx]
        elif cls is Maybe:
            return (Just if arg else Wrong)(arg)
        elif isinstance(arg, cls):
            return arg
        elif not isinstance(arg, Maybe):
            self = super(Maybe, cls).__new__(cls)
            self.inner = arg
            return self
        else:
            msg = 're-wrapping inverted value: {}({})'
            raise ValueError(msg.format(cls.__name__, arg))

    def __init__(self, *args):
        pass

    def __nonzero__(self):
        return isinstance(self, Just)
    __bool__ = __nonzero__

    def __str__(self):
        return '{}({!r})'.format(type(self).__name__, self.inner)
    __repr__ = __str__

    def __eq__(self, other):
        return (isinstance(other, type(self)) and self.inner == other.inner or
                self.inner is other)    # TODO: check if `==` instead `is`

    def __ne__(self, other):
        return not (self == other)


class Just(Maybe):
    '''A wrapper for valid results.'''
    __slots__ = ()


class Wrong(Maybe):
    '''A wrapper for invalid results.

    When encapsulation errors, the current trace-back is properly encapsulated
    using `xoutil.eight.exceptions`:mod: module features.

    # TODO: Use `naught` or `Left` instead.

    '''
    __slots__ = ()

    def __new__(cls, *args):
        self = super(Wrong, cls).__new__(cls, *args)
        if isinstance(self.inner, BaseException):
            from xoutil.eight.exceptions import with_traceback
            from sys import exc_info
            info = exc_info()
            if info[1] is self.inner:
                self.inner = with_traceback(self.inner, info[2])
        return self


# ---- special singletons ----

_false = Wrong()
_true = Just()
_none = Wrong(None)
