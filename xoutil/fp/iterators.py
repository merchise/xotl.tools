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


def iter_compose(*fs):
    '''Compose functions that take an item and return an iterator.

    For two functions, ``iter_compose(g, f)`` is roughly equivalent to::

       lambda x: (z for y in f(x) for z in g(y))

    In general this is, ``reduce(_compose, fs, lambda x: [x])``; where
    ``_compose`` is the lambda for two arguments.

    .. versionadded:: 1.9.6

    '''
    def _compose(g, f):
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
        return _compose(*fs)
    else:
        return reduce(_compose, fs, lambda x: [x])
