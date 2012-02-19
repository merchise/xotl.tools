# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.types
#----------------------------------------------------------------------
# Copyright (c) 2010-2011 Merchise Autrement
# All rights reserved.
#
# Author: Medardo Rodriguez
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.


'''
Utilities for types and the like.
'''


from __future__ import (division as _py3_division, print_function as _py3_print,
                        unicode_literals as _py3_unicode)

from xoutil.data import smart_copy

_legacy = __import__(b'types', fromlist=[b'dummy'], level=0)
GeneratorType = _legacy.GeneratorType
smart_copy(_legacy , __import__(__name__, fromlist=[b'_legacy']))
del _legacy


class _UnsetType(type):
    def __nonzero__(self):
        return False


class Unset:
    '''
    To be used as default value to be sure none is returned in scenarios
    where "None" could be a valid value.

    For example:
        >>> getattr('', '__doc__', Unset) is Unset
        False
    '''
    __metaclass__ = _UnsetType

    def __new__(cls, *args, **kwargs):
        raise TypeError("cannot create 'Unset' instances")



def is_iterable(maybe):
    '''
    Tests `maybe` to see if it is list like::
    
        >>> is_iterable('all strings are iterable')
        True
        
        # Numbers are not
        >>> is_iterable(1)
        False
        
        >>> is_iterable(xrange(1))
        True
        
        >>> is_iterable({})
        True
        
        >>> is_iterable(tuple())
        True
        
        >>> is_iterable(set())
        True
    '''
    try:
        iter(maybe)
    except:
        return False
    else:
        return True


def is_collection(maybe):
    '''
    Test value to see if it is a tuple, a list, a set or a generator function.
    It's False for dictionaries or strings::
        >>> is_collection('all strings are iterable')
        False
        
        # Numbers are not
        >>> is_collection(1)
        False
        
        >>> is_collection(xrange(1))
        True
        
        >>> is_collection({})
        False
        
        >>> is_collection(tuple())
        True
        
        >>> is_collection(set())
        True
        
        >>> is_collection(a for a in xrange(100))
        True
    '''
    return isinstance(maybe, (tuple, xrange, list, set, frozenset,
                              GeneratorType))


def is_string_like(maybe):
    '''Test value to see if it acts like a string'''
    try:
        maybe + ""
    except TypeError:
        return False
    else:
        return True


def is_scalar(maybe):
    '''Test to see value is a string, an int, or some other scalar type'''
    return is_string_like(maybe) or not is_iterable(maybe)
