# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.types
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# Copyright (c) 2010-2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.


'''
This modules mirrors all the functions (and, in general, objects) from the
standard library module ``types``; but it also includes several new types and
type-related functions.
'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from xoutil.modules import copy_members as _copy_python_module_members
_copy_python_module_members()
del _copy_python_module_members

from xoutil.compat import xrange_
from xoutil.string import names as _names


class UnsetType(object):
    '''The unique instance `Unset` is to be used as default value to be sure
    none is returned in scenarios where `None` could be a valid value.

    For example::

        >>> getattr('', '__doc__', Unset) is Unset
        False

    '''
    __slots__ = (str('name'), )

    def __new__(cls, name, **kwargs):
        if kwargs.get('__singleton__', None) is UnsetType:
            result = super(UnsetType, cls).__new__(cls)
            result.name = name
            return result
        else:
            raise TypeError("cannot create 'UnsetType' instances")

    def __nonzero__(self):
        return False

    def __repr__(self):
        return self.name
    __str__ = __repr__


Unset = UnsetType('Unset', __singleton__=UnsetType)

#: To be used in arguments that are currently ignored cause they are being
#: deprecated. The only valid reason to use `ignored` is to signal ignored
#: arguments in method's/function's signature.
ignored = UnsetType('ignored', __singleton__=UnsetType)


#: The type of methods that are builtin in Python.
WrapperDescriptorType = SlotWrapperType = type(object.__getattribute__)


class mro_dict(object):
    '''An utility class that behaves like a read-only dict to query the
    attributes in the mro chain of a class (or object).

    '''
    def __init__(self, target):
        t = target if hasattr(target, 'mro') else type(target)
        self._target_mro = t.mro()

    def __getitem__(self, name):
        return self.get(name)

    def get(self, name, default=Unset):
        from xoutil.objects import get_first_of
        probes = tuple(c.__dict__ for c in self._target_mro)
        result = get_first_of(probes, name, default=Unset)
        if result is Unset:
            if default is Unset:
                raise KeyError(name)
            else:
                return default
        else:
            return result


def is_iterable(maybe):
    '''
    Returns True if `maybe` an iterable object (e.g. implements the `__iter__`
    method:)

    ::

        >>> is_iterable('all strings are iterable')
        True

        # Numbers are not
        >>> is_iterable(1)
        False

        >>> is_iterable(xrange_(1))
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
    Test `maybe` to see if it is a tuple, a list, a set or a generator
    function.
    It returns False for dictionaries and strings::

        >>> is_collection('all strings are iterable')
        False

        # Numbers are not
        >>> is_collection(1)
        False

        >>> is_collection(xrange_(1))
        True

        >>> is_collection({})
        False

        >>> is_collection(tuple())
        True

        >>> is_collection(set())
        True

        >>> is_collection(a for a in xrange_(100))
        True
    '''
    return isinstance(maybe, (tuple, xrange_, list, set, frozenset,
                              GeneratorType))


def is_string_like(maybe):
    '''Returns True if `maybe` acts like a string'''
    try:
        maybe + ""
    except TypeError:
        return False
    else:
        return True


def is_scalar(maybe):
    '''Returns True if `maybe` is a string, an int, or some other scalar type
    (i.e not an iterable.)

    '''
    return is_string_like(maybe) or not is_iterable(maybe)


def is_staticmethod(desc, name=Unset):
    '''Returns true if a `method` is a static method.

    This function takes the same arguments as :func:`is_classmethod`.

    '''
    if name:
        desc = mro_dict(desc).get(name, None)
    return isinstance(desc, staticmethod)


def is_classmethod(desc, name=Unset):
    '''Returns true if a `method` is a class method.

    :param desc: This may be the method descriptor or the class that holds the
                 method, in the second case you must provide the `name` of the
                 method.

                 .. note::

                    Notice that in the first case what is needed is the
                    **method descriptor**, i.e, taken from the class'
                    `__dict__` attribute. If instead you pass something like
                    ``cls.methodname``, this method will return False whilst
                    :func:`is_instancemethod` will return True.

    :param name: The name of the method, if the first argument is the class.

    '''
    if name:
        desc = mro_dict(desc).get(name, None)
    return isinstance(desc, classmethod)


def is_instancemethod(desc, name=Unset):
    '''Returns true if a given `method` is neither a static method nor a class
    method.

    This function takes the same arguments as :func:`is_classmethod`.

    '''
    from types import FunctionType
    if name:
        desc = mro_dict(desc).get(name, None)
    return isinstance(desc, FunctionType)


def is_slotwrapper(desc, name=Unset):
    '''Returns True if a given `method` is a slot wrapper (i.e. a method that
    is builtin in the `object` base class).

    This function takes the same arguments as :func:`is_classmethod`.

    '''
    if name:
        desc = mro_dict(desc).get(name, None)
    return isinstance(desc, SlotWrapperType)


__all__ = _names('Unset', 'ignored', 'is_iterable', 'is_collection',
                 'is_scalar', 'is_string_like')
