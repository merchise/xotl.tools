#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Implements the meta() function using the Py3k syntax.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

from . import _py3
assert _py3, 'This module should be loaded in Py3k only'


def metaclass(meta, **kwargs):
    from ._meta import Mixin

    if isinstance(meta, type) and issubclass(meta, type) and meta is not type:
        metabase = meta.__base__
    else:
        metabase = type

    class inner_meta(metabase):
        @classmethod
        def __prepare__(cls, name, bases, **kwargs):
            real = name != '__inner__'
            prepare = getattr(meta, '__prepare__', None) if real else None
            return prepare(name, bases, **kwargs) if prepare else dict()

        def __new__(cls, name, bases, attrs, **kw):
            if name != '__inner__':
                bases = tuple(b for b in bases if Mixin not in b.__bases__)
                return meta(name, bases, attrs)
            else:
                return type.__new__(cls, name, bases, attrs)

        def __init__(self, name, bases, attrs, **kw):
            pass

    from ._types import new_class
    kwds = dict(kwargs, metaclass=inner_meta)
    return new_class('__inner__', (Mixin, ), kwds=kwds)
