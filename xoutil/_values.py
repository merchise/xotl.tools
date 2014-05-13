#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil._values
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-04-12

'''Fixed values like Unset, Ignored, Required, etc...
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)


class UnsetType(object):
    '''The unique instance `Unset` is to be used as default value to be sure
    `None` is returned in scenarios where `None` could be a valid value.

    For example::

        >>> class X(object):
        ...      attr = None

        >>> getattr(X(), 'attr', Unset) is Unset
        False

    '''
    __slots__ = (str('name'), str('__name__'), )

    def __new__(cls, name, **kwargs):
        if kwargs.get('__singleton__', None) is UnsetType:
            result = super(UnsetType, cls).__new__(cls)
            result.__name__ = result.name = str(name)
            return result
        else:
            raise TypeError("cannot create 'UnsetType' instances")

    def __nonzero__(self):
        return False
    __bool__ = __nonzero__

    def __repr__(self):
        return self.name
    __str__ = __repr__


Unset = UnsetType('Unset', __singleton__=UnsetType)

#: To be used in arguments that are currently ignored cause they are being
#: deprecated. The only valid reason to use `ignored` is to signal ignored
#: arguments in method's/function's signature.
Ignored = UnsetType('Ignored', __singleton__=UnsetType)
