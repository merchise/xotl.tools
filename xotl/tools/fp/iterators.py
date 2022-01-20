#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Functional tools for functions that returns iterators (generators, etc.)

.. warning:: This module is experimental.  It may be removed completely, moved
   or otherwise changed.

"""
from functools import reduce
from typing import Callable, Iterable, TypeVar

X = TypeVar("X")
Y = TypeVar("Y")
Z = TypeVar("Z")
T = TypeVar("T")


def kleisli_compose(*fs: Callable[[T], Iterable[T]]) -> Callable[[T], Iterable[T]]:
    """The Kleisli composition operator (right-to-left version).

    For two functions, ``kleisli_compose(g, f)`` returns::

       lambda x: (z for y in f(x) for z in g(y))

    In general this is, ``reduce(_compose, fs, lambda x: [x])``; where
    ``_compose`` is the lambda for two arguments.

    .. note:: Despite name (Kleisli), Python does not have a true Monad_
       type-class.  So this function works with functions taking a single
       argument and returning an iterator -- it also works with iterables.

    .. _Monad: https://en.wikipedia.org/wiki/Monad_(functional_programming)

    .. versionadded:: 1.9.6
    .. versionchanged:: 1.9.7 Name changed to ``kleisli_compose``.

    .. warning:: You may want to use `kleisli_compose_foldl`:func: which
       matches the order semantics of the functional kleisli composition
       ``>=>``.

    """

    def _kleisli_compose(
        g: Callable[[Y], Iterable[Z]], f: Callable[[X], Iterable[Y]]
    ) -> Callable[[X], Iterable[Z]]:
        # (>>.) :: Monad m => (b -> m c) -> (a -> m b) -> a -> m c
        # g >>. f = \x -> f x >>= g
        #
        # In the list monad:
        #
        # g >>. f = \x -> concat (map g (f x))
        return lambda x: (z for y in f(x) for z in g(y))

    if len(fs) == 2:
        # optimize a bit so that we can avoid the 'lambda x: [x]' for common
        # cases.
        return _kleisli_compose(*fs)
    else:
        return reduce(_kleisli_compose, fs, lambda x: iter([x]))


def kleisli_compose_foldl(*fs: Callable[[T], Iterable[T]]) -> Callable[[T], Iterable[T]]:
    """Same as `kleisli_compose`:func: but composes left-to-right.

    Examples:

      >>> s15 = lambda s: tuple(s + str(i) for i in range(1, 5))
      >>> s68 = lambda s: tuple(s + str(i) for i in range(6, 8))

      >>> # kleisli_compose produces "6" >>= 1, 2, 3, 4; and then "7" >>= 1, 2, 3, 4
      >>> list(kleisli_compose(s15, s68)(""))
      ['61', '62', '63', '64', '71', '72', '73', '74']

      >>> list(kleisli_compose_foldl(s15, s68)(""))
      ['16', '17', '26', '27', '36', '37', '46', '47']

    If the operation is non-commutative (as the string concatenation) you end
    up with very different results.

      >>> n15 = lambda s: tuple(s + i for i in range(1, 5))
      >>> n68 = lambda s: tuple(s + i for i in range(6, 8))

      >>> list(kleisli_compose(n15, n68)(0))
      [7, 8, 9, 10, 8, 9, 10, 11]

      >>> list(kleisli_compose_foldl(n15, n68)(0))
      [7, 8, 8, 9, 9, 10, 10, 11]

    If the operation is commutative you get the same *set* of results, but the
    order may be different.

    """
    # This basically the same as _kleisli_compose above but with f and g
    # swapped.
    #
    # In our derivation of
    def _kleisli_compose_foldl(f, g):
        return lambda x: (z for y in f(x) for z in g(y))

    if len(fs) == 2:
        # optimize a bit so that we can avoid the 'lambda x: [x]' for common
        # cases.
        return _kleisli_compose_foldl(*fs)
    else:
        return reduce(_kleisli_compose_foldl, fs, lambda x: iter([x]))
