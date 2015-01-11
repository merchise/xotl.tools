#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil._values
# ---------------------------------------------------------------------
# Copyright (c) 2013-2015 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-04-12

'''Fixed special values like Unset, Ignored, Required, etc...

All these values are False but are intended in places where None could be a
valid value.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)


class UnsetType(object):
    '''Instances are unique by name (singletons).

    Special instance `Unset` is automatically created and intended to be used
    as default value to be sure `None` is returned in scenarios it could be a
    valid value.

    For example::

        >>> class X(object):
        ...      attr = None

        >>> getattr(X(), 'attr', Unset) is Unset
        False

    '''
    __slots__ = tuple(str(slot) for slot in ('name', '__name__', 'help'))
    __instances__ = {}

    def __new__(cls, name, **kwargs):
        klass = kwargs.pop('__singleton__', None)
        help = kwargs.pop('help', None)
        if (not kwargs and (klass is UnsetType) and (cls is klass) and
                (__name__ == cls.__module__)):
            self = cls.__instances__.get(name)
            if self is None:
                self = super(UnsetType, cls).__new__(cls)
                self.__name__ = self.name = str(name)
                self.help = help
                cls.__instances__[name] = self
            return self
        else:
            raise TypeError("cannot create 'UnsetType' instances")

    def __nonzero__(self):
        return False

    __bool__ = __nonzero__

    def __repr__(self):
        return self.name

    __str__ = __repr__


Unset = UnsetType('Unset', __singleton__=UnsetType,
                  help='False value where None could be a valid value.')

Undefined = UnsetType('Undefined', __singleton__=UnsetType,
                      help=('False value for local scope use or where Unset '
                            'could be a valid value.'))

Ignored = UnsetType('Ignored', __singleton__=UnsetType,
                    help=("To be used in arguments that are currently "
                          "ignored cause they are being deprecated. The "
                          "only valid reason to use `ignored` is to signal "
                          "ignored arguments in method's/function's "
                          "signature."))
