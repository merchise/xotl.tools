#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.clutter.values
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created 2015-02-26

'''Special serialization values.

Types for values represented with a name prefix plus a space.

JSON ``true` and ``false`` as logical instances.

For example: ``uint16 128``.  Like in ``dconf`` integer representations.

All integers compatible with ``dconf`` are defined (`uint16`, `uint32`,
`uint64`, `int16`, `int32` and `int64`).

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

from xoutil import Unset


__docstring_format__ = 'rst'


class Prefixed(object):
    '''Base class for values represented with a name prefix.'''

    __slots__ = ()

    def __repr__(self):
        prefix = type(self).__name__
        return str('%s %s' % (prefix, int(self)))

    __str__ = __repr__

    @staticmethod
    def parse(value):
        '''Returns a value of a proper type.'''
        values = (cls.eval(value) for cls in Prefixed.iter_types())
        return next((res for res in values if res is not Unset), Unset)

    @classmethod
    def eval(cls, value):
        '''Return a int object from a string.

        If value is not valid for this type, returns `Unset`.

        '''
        prefix = '%s ' % cls.__name__
        if value.startswith(prefix):
            value = value[len(prefix):].strip()
            if '#' in value:    # Remove comment
                value = value.split('#')[0].strip()
            return cls(value)
        else:
            return Unset

    @classmethod
    def iter_types(cls):
        '''Iterate types that must be parsed.'''
        for item in cls.__subclasses__():
            yield item
            for inner in item.iter_types():
                yield inner


def check_int(value, low, high):
    '''Auxiliary function to check all integers.'''
    if low <= value <= high:
        return value
    else:
        msg = 'Invalid "%s", must be between "%s" and "%s"!'
        raise ValueError(msg % (value, low, high))


class uint8(Prefixed, int):
    '''Unsigned integer, 8 bits'''

    __slots__ = ()

    def __new__(cls, value=0):
        self = super(uint16, cls).__new__(cls, value)
        return check_int(self, 0, 2**8 - 1)


class uint16(Prefixed, int):
    '''Unsigned integer, 16 bits'''

    __slots__ = ()

    def __new__(cls, value=0):
        self = super(uint16, cls).__new__(cls, value)
        return check_int(self, 0, 2**16 - 1)


class uint32(Prefixed, int):
    '''Unsigned integer, 32 bits'''

    __slots__ = ()

    def __new__(cls, value=0):
        self = super(uint32, cls).__new__(cls, value)
        return check_int(self, 0, 2**32 - 1)


class uint64(Prefixed, int):
    '''Unsigned integer, 64 bits'''

    __slots__ = ()

    def __new__(cls, value=0):
        self = super(uint64, cls).__new__(cls, value)
        return check_int(self, 0, 2**64 - 1)


class int8(Prefixed, int):
    '''Signed integer, 8 bits'''

    __slots__ = ()

    def __new__(cls, value=0):
        self = super(int16, cls).__new__(cls, value)
        limit = 2**7
        return check_int(self, -limit, limit - 1)


class int16(Prefixed, int):
    '''Signed integer, 16 bits'''

    __slots__ = ()

    def __new__(cls, value=0):
        self = super(int16, cls).__new__(cls, value)
        limit = 2**15
        return check_int(self, -limit, limit - 1)


class int32(Prefixed, int):
    '''Signed integer, 32 bits'''

    __slots__ = ()

    def __new__(cls, value=0):
        self = super(int32, cls).__new__(cls, value)
        limit = 2**31
        return check_int(self, -limit, limit - 1)


class int64(Prefixed, int):
    '''Unsigned integer, 64 bits'''

    __slots__ = ()

    def __new__(cls, value=0):
        self = super(int64, cls).__new__(cls, value)
        limit = 2**63
        return check_int(self, -limit, limit - 1)


# Logical instances

from xoutil.logical import Logical

false = Logical('false')

true = Logical('true', True)

del Logical
