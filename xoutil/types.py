# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.types
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
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

_pm = _copy_python_module_members()
GeneratorType = _pm.GeneratorType
FunctionType = _pm.FunctionType
ModuleType = _pm.ModuleType

del _pm, _copy_python_module_members


from xoutil import Unset as _unset
from collections import Mapping

# FIXME: [med] Reintroduce UnsetType or deprecate it here.
from xoutil.logical import Logical as UnsetType    # noqa

from xoutil.names import strlist as strs
__all__ = strs('mro_dict', 'UnsetType', 'DictProxyType',
               'SlotWrapperType', 'is_iterable', 'is_collection',
               'is_string_like', 'is_scalar', 'is_staticmethod',
               'is_classmethod', 'is_instancemethod', 'is_slotwrapper',
               'is_module', 'Required', 'NoneType', 'new_class',
               'prepare_class')
del strs


from .eight.types import (DictProxyType, MemberDescriptorType,    # noqa
                          NoneType, MappingProxyType, SimpleNamespace,
                          DynamicClassAttribute, new_class, prepare_class,
                          _calculate_meta)


#: The type of methods that are builtin in Python.
#:
#: This is roughly the type of the ``object.__getattribute__`` method.
WrapperDescriptorType = SlotWrapperType = type(object.__getattribute__)


try:
    from exceptions import StandardError
except:
    StandardError = Exception


class mro_dict(Mapping):
    '''An utility class that behaves like a read-only dict to query the
    attributes in the MRO chain of a `target` class (or an object's class).

    '''
    def __init__(self, target):
        type_ = target if hasattr(target, 'mro') else type(target)
        self._target_mro = type_.mro()

    def __getitem__(self, name):
        from xoutil.objects import get_first_of
        probes = tuple(c.__dict__ for c in self._target_mro)
        result = get_first_of(probes, name, default=_unset)
        if result is not _unset:
            return result
        else:
            raise KeyError(name)

    def __iter__(self):
        res = []
        probes = tuple(c.__dict__ for c in self._target_mro)
        for probe in probes:
            for key in probe:
                if key not in res:
                    res.append(key)
                    yield key

    def __len__(self):
        return sum(1 for _ in self)


# TODO: Many of is_*method methods here are needed to be compared against the
# standard lib's module inspect versions.  If they behave the same, these
# should be deprecated in favor of the standards.

def is_iterable(maybe):
    '''Returns True if `maybe` is an iterable object (e.g. implements the
    `__iter__` method):

    ::

        >>> is_iterable('all strings are iterable')
        True

        # Numbers are not
        >>> is_iterable(1)
        False

        >>> from six.moves import range
        >>> is_iterable(range(1))
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
    '''Test `maybe` to see if it is a tuple, a list, a set or a generator
    function.

    It returns False for dictionaries and strings::

        >>> is_collection('all strings are iterable')
        False

        # Numbers are not
        >>> is_collection(1)
        False

        >>> from six.moves import range
        >>> is_collection(range(1))
        True

        >>> is_collection({})
        False

        >>> is_collection(tuple())
        True

        >>> is_collection(set())
        True

        >>> is_collection(a for a in range(100))
        True

    .. versionchanged:: 1.5.5 UserList are collections.

    '''
    from xoutil.collections import UserList
    from six.moves import range
    return isinstance(maybe, (tuple, range, list, set, frozenset,
                              GeneratorType, UserList))


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


def is_staticmethod(desc, name=_unset):
    '''Returns true if a `method` is a static method.

    This function takes the same arguments as :func:`is_classmethod`.

    '''
    if name:
        desc = mro_dict(desc).get(name, None)
    return isinstance(desc, staticmethod)


def is_classmethod(desc, name=_unset):
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


def is_instancemethod(desc, name=_unset):
    '''Returns true if a given `method` is neither a static method nor a class
    method.

    This function takes the same arguments as :func:`is_classmethod`.

    '''
    if name:
        desc = mro_dict(desc).get(name, None)
    return isinstance(desc, FunctionType)


def is_slotwrapper(desc, name=_unset):
    '''Returns True if a given `method` is a slot wrapper (i.e. a method that
    is builtin in the `object` base class).

    This function takes the same arguments as :func:`is_classmethod`.

    '''
    if name:
        desc = mro_dict(desc).get(name, None)
    return isinstance(desc, SlotWrapperType)


def is_module(maybe):
    '''Returns True if `maybe` is a module.'''
    return isinstance(maybe, ModuleType)


class Required(object):
    '''A type for required fields in scenarios where a default is not
    possible.

    '''
    def __init__(self, *args, **kwargs):
        pass


# Real "Py4k" signature ``are_instances(*subjects, types)``.
def are_instances(*args):
    '''Return True if every `subject` is an instance of (any) `types`.

    :param subjects: All but last positional arguments.  Are the objects
        required to be instances of `types`.

    :param types: The last positional argument.  Either a single type or a
       sequence of types.  This must meet the conditions on the last argument
       of `isinstance`:func:.

    :returns: True or False.  True if for every `subject`,
       ``isinstance(subject, types)`` is True.  Otherwise, False.

    If no `subjects` are provided return True::

        >>> are_instances(int)
        True

    .. seealso:: The function :func:`no_instances` allows to test for subjects
                 not being instances of types.

    '''
    if not args:
        raise TypeError('are_instances requires at least an argument')
    subjects, types = args[:-1], args[-1]
    if not subjects:
        isinstance(None, types)   # HACK: always validate `types`.
    return all(isinstance(subject, types) for subject in subjects)


# Real Py4k signature ``are_instances(*subjects, types)``self.
def no_instances(*args):
    '''Return True if every `subject` is **not** an instance of (neither)
    `types`.

    :param subjects: All but last positional arguments.  Are the objects
        required not to be instances of `types`.

    :param types: The last positional argument.  Either a single type or a
       sequence of types.  This must meet the conditions on the last argument
       of `isinstance`:func:.

    :returns: True or False.  True if for every `subject`,
       ``isinstance(subject, types)`` is False.  Otherwise, False.

    If no `subjects` are provided return True::

        >>> no_instances(int)
        True

    .. note:: This is not the same as ``not are_instances(...)``.

       This function requires that *no* subject is an instance of `types`.
       Negating :func:`are_instances` would be True if *any* subject is not an
       instance of `types`.

    '''
    if not args:
        raise TypeError('no_instances requires at least an argument')
    subjects, types = args[:-1], args[-1]
    if not subjects:
        isinstance(None, types)   # HACK: always validate `types`.
    return all(not isinstance(subject, types) for subject in subjects)
