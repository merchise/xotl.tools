#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
'''Functional tools for functions that returns iterators (generators, etc.)

.. warning:: This module is experimental.  It may be removed completely, moved
   or otherwise changed.

'''
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from functools import reduce
from xoutil.deprecation import deprecated


def kleisli_compose(*fs):
    '''The Kleisli composition operator.

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

    '''
    def _kleisli_compose(g, f):
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


iter_compose = deprecated(kleisli_compose)(kleisli_compose)
