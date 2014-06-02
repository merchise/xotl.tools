# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.types
#----------------------------------------------------------------------
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


from xoutil._values import Unset as _unset
from collections import Mapping

# FIXME: [med] Reintroduce UnsetType or deprecate it here.
from xoutil._values import UnsetType

from xoutil.names import strlist as strs
__all__ = strs('mro_dict', 'UnsetType', 'DictProxyType',
               'SlotWrapperType', 'is_iterable', 'is_collection',
               'is_string_like', 'is_scalar', 'is_staticmethod',
               'is_classmethod', 'is_instancemethod', 'is_slotwrapper',
               'is_module', 'Required', 'NoneType', 'new_class',
               'prepare_class')
del strs

#: The type of methods that are builtin in Python.
#:
#: This is roughly the type of the ``object.__getattribute__`` method.
WrapperDescriptorType = SlotWrapperType = type(object.__getattribute__)


#: A compatible Py2 and Py3k DictProxyType, since it does not exists in Py3k.
DictProxyType = type(object.__dict__)

import sys
_pypy = hasattr(sys, 'pypy_version_info')
if _pypy:
    class _foo(object):
        __slots__ = 'bar'
    MemberDescriptorType = type(_foo.bar)
    del _foo
del _pypy


# In Py3.3 NoneType is not defined in the stdlib `types` module. This solves
# the issue.
NoneType = type(None)

if sys.version_info < (3, 3):
    from xoutil.collections import MappingView, MutableMapping

    class MappingProxyType(MappingView, MutableMapping):
        def __init__(self, mapping):
            if not isinstance(mapping, Mapping):
                raise TypeError
            super(MappingProxyType, self).__init__(mapping)

        def items(self):
            from xoutil.collections import ItemsView
            try:
                items = type(self._mapping).__dict__['items']
                if items is not dict.__dict__['items']:
                    return items(self._mapping)
                else:
                    return ItemsView(self)
            except KeyError:
                return ItemsView(self)

        def keys(self):
            from xoutil.collections import KeysView
            try:
                keys = type(self._mapping).__dict__['keys']
                if keys is not dict.__dict__['keys']:
                    return keys(self._mapping)
                else:
                    return KeysView(self)
            except KeyError:
                return KeysView(self)

        def values(self):
            from xoutil.collections import ValuesView
            try:
                values = type(self._mapping).__dict__['values']
                if values is not dict.__dict__['values']:
                    return values(self._mapping)
                else:
                    return ValuesView(self)
            except KeyError:
                return ValuesView(self)

        def __iter__(self):
            return iter(self._mapping)

        def get(self, key, default=None):
            return self._mapping.get(key, default)

        def __contains__(self, key):
            return key in self._mapping

        def copy(self):
            return self._mapping.copy()

        def __dir__(self):
            return [
                '__contains__',
                '__getitem__',
                '__iter__',
                '__len__',
                'copy',
                'get',
                'items',
                'keys',
                'values',
            ]

        def __getitem__(self, key):
            return self._mapping[key]

        def __setitem__(self, key, value):
            self._mapping[key] = value

        def __delitem__(self, key):
            del self._mapping[key]


if sys.version_info < (3, 4):
    class SimpleNamespace(object):
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

        def __eq__(self, other):
            return self.__dict__ == other.__dict__

        from xoutil.reprlib import recursive_repr

        @recursive_repr(str('namespace(...)'))
        def __repr__(self):
            keys = sorted(self.__dict__)
            items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
            return "{}({})".format('namespace', ", ".join(items))

    class DynamicClassAttribute(object):
        """Route attribute access on a class to :meth:`~object.__getattr__`.

        This is a descriptor, used to define attributes that act differently
        when accessed through an instance and through a class.  Instance
        access remains normal, but access to an attribute through a class will
        be routed to the class's :meth:`~object.__getattr__` method; this is
        done by raising AttributeError.

        This allows one to have properties active on an instance, and have
        virtual attributes on the class with the same name (see
        :class:`~py3:enum.Enum` for an example).

        .. versionadded:: 1.5.5

        .. note:: The class Enum mentioned has not yet been backported.

        .. note:: In Python 3.4+ this is an alias to
                  :func:`types.DynamicClassAttribute
                  <py3:types.DynamicClassAttribute>`.

        """
        def __init__(self, fget=None, fset=None, fdel=None, doc=None):
            self.fget = fget
            self.fset = fset
            self.fdel = fdel
            # next two lines make DynamicClassAttribute act the same as
            # property
            self.__doc__ = doc or fget.__doc__
            self.overwrite_doc = doc is None
            # support for abstract methods
            self.__isabstractmethod__ = bool(getattr(fget, '__isabstractmethod__', False))

        def __get__(self, instance, ownerclass=None):
            if instance is None:
                if self.__isabstractmethod__:
                    return self
                raise AttributeError()
            elif self.fget is None:
                raise AttributeError("unreadable attribute")
            return self.fget(instance)

        def __set__(self, instance, value):
            if self.fset is None:
                raise AttributeError("can't set attribute")
            self.fset(instance, value)

        def __delete__(self, instance):
            if self.fdel is None:
                raise AttributeError("can't delete attribute")
            self.fdel(instance)

        def getter(self, fget):
            fdoc = fget.__doc__ if self.overwrite_doc else None
            result = type(self)(fget, self.fset, self.fdel, fdoc or self.__doc__)
            result.overwrite_doc = self.overwrite_doc
            return result

        def setter(self, fset):
            result = type(self)(self.fget, fset, self.fdel, self.__doc__)
            result.overwrite_doc = self.overwrite_doc
            return result

        def deleter(self, fdel):
            result = type(self)(self.fget, self.fset, fdel, self.__doc__)
            result.overwrite_doc = self.overwrite_doc
            return result


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

        >>> from xoutil.six.moves import range
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

        >>> from xoutil.six.moves import range
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
    from xoutil.six.moves import range
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

    See also :func:`no_instances`.

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

    See also :func:`are_instances`.

    '''
    if not args:
        raise TypeError('no_instances requires at least an argument')
    subjects, types = args[:-1], args[-1]
    if not subjects:
        isinstance(None, types)   # HACK: always validate `types`.
    return all(not isinstance(subject, types) for subject in subjects)


if sys.version_info < (3, 3):
    # PEP 3115 compliant dynamic class creation.  Used in
    # xoutil.objects.metaclass
    #
    # Taken from Python 3.3 code-base.
    #
    def new_class(name, bases=(), kwds=None, exec_body=None):
        """Create a class object dynamically using the appropriate metaclass.

        """
        import sys
        meta, ns, kwds = prepare_class(name, bases, kwds)
        if exec_body is not None:
            exec_body(ns)
        if sys.version_info >= (3, 0):
            return meta(name, bases, ns, **kwds)
        else:
            return meta(name, bases, ns)

    def prepare_class(name, bases=(), kwds=None):
        """Call the __prepare__ method of the appropriate metaclass.

        Returns (metaclass, namespace, kwds) as a 3-tuple

        *metaclass* is the appropriate metaclass
        *namespace* is the prepared class namespace
        *kwds* is an updated copy of the passed in kwds argument with any
        'metaclass' entry removed. If no kwds argument is passed in, this will
        be an empty dict.

        """
        if kwds is None:
            kwds = {}
        else:
            kwds = dict(kwds)  # Don't alter the provided mapping
        meta = kwds.pop('metaclass', None)
        if not meta:
            if bases:
                meta = type(bases[0])
            else:
                meta = type
        if isinstance(meta, type):
            # when meta is a type, we first determine the most-derived
            # metaclass instead of invoking the initial candidate directly
            meta = _calculate_meta(meta, bases)
        if hasattr(meta, '__prepare__'):
            ns = meta.__prepare__(name, bases, **kwds)
        else:
            ns = {}
        return meta, ns, kwds

    def _calculate_meta(meta, bases):
        """Calculate the most derived metaclass."""
        winner = meta
        for base in bases:
            base_meta = type(base)
            if issubclass(winner, base_meta):
                continue
            if issubclass(base_meta, winner):
                winner = base_meta
                continue
            # else:
            raise TypeError("metaclass conflict: "
                            "the metaclass of a derived class "
                            "must be a (non-strict) subclass "
                            "of the metaclasses of all its bases")
        return winner

del sys
