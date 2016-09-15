# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.future.types
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise and Contributors
# All rights reserved.
#
# This module was started in 2010 by Medardo Rodríguez,
# Copyrighted 2013, 2014 by Merchise Autrement, and 2015-2016 by Merchise
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-09-11

'''Extends the standard `types` module.

Standard module defines names for all type symbols known in the standard
interpreter.

This modules mirrors all the functions (and, in general, objects) from the
standard library module `types`:mod:; but it also includes several new types
and type-related functions.

This module unifies old `xoutil.types`:mod: and `xoutil.eigth.types`:mod:
modules, which are deprecated now.

There are some symbols included in Python 2.x series, but not in Python 3 that
we don't include here:

- `TypeType`: use `type` instead

- `ObjectType`: use `object`

- `IntType`: use `int`

- `LongType`: use `long` in Python 2 and `int` in Python 3; better see
  `xoutil.eight.integer_types` definition.

- `FloatType`: use `float`

- `BooleanType`: use `bool`

- `ComplexType`: use `complex`

- `StringType`: use str

- `UnicodeType`: use `unicode` in Python 2 and `str` in Python 3; there are
  two aliases for that: `xoutil.eigth.UnicodeType` and
  `xoutil.eigth.text_type`.

- `StringTypes`: use `xoutil.eigth.StringTypes`or
  `xoutil.eigth.string_types`.

- `BufferType`: use `buffer` in Python 2 and `memoryview` in Python 3; there
  is an alias for this convention in `xoutil.eigth.buffer`.  The
  `memoryview`:class: API is similar but not exactly the same as that of
  `buffer`.

- `TupleType`: use `tuple`

- `ListType`: use `list`

- `DictType` (or `DictionaryType`): use `dict`

- `ClassType`: Python 2 old-style classes, don't exists in Python 3, see
  `xoutil.eigth.ClassTypes`.

- `InstanceType`: type of instances of Python 2 old-style classes, don't
  exists in Python 3, see `xoutil.eigth.typeof`.

- `UnboundMethodType`: use `~types.MethodType` alias

- `FileType`: use `file`

- `XRangeType` (or `xrange`): in Python 3 `range` always returns a generator
  object; use `xoutil.eigth.range`:class: for compatibility; wraps it with
  list (``list(range(...))``) to obtain old `range` style

- `SliceType`: use `slice`

- In Jython and PyPy, `MemberDescriptorType` is identical to
  `GetSetDescriptorType`; to mantain compatibility in some `xoutil` code, they
  are differentiated in this module.

- `CoroutineType` and `coroutine`: use new Python 3 `async` statement; not
  implementable in Python 2.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.future import _rectify
_rectify.check()
del _rectify

from xoutil.eight import _py2, _py34    # noqa
from types import *    # noqa
from types import __all__    # noqa

__all__ = list(__all__)    # copy it to avoid errors

try:
    NoneType
except NameError:
    NoneType = type(None)
    __all__.append('NoneType')

try:
    EllipsisType
except NameError:
    EllipsisType = type(Ellipsis)
    __all__.append('EllipsisType')

# TODO: `MappingProxyType` is the Python 3 equivalent for `DictProxyType` in
# Python 2.  Deprecate `DictProxyType` in favor of `MappingProxyType`.
try:
    DictProxyType
except NameError:
    DictProxyType = type(type.__dict__)
    __all__.append('DictProxyType')

try:
    MappingProxyType
except NameError:
    MappingProxyType = type(type.__dict__)
    __all__.append('MappingProxyType')

if _py2:
    from collections import Mapping
    if not issubclass(MappingProxyType, Mapping):
        # TODO: when implement `xoutil.future.collections`, fix this problem
        # there.
        Mapping.register(MappingProxyType)
    del Mapping

try:
    NotImplementedType
except NameError:
    NotImplementedType = type(NotImplemented)
    __all__.append('NotImplementedType')


# Check Jython and PyPy peculiarity
if MemberDescriptorType is GetSetDescriptorType:
    class _foo(object):
        __slots__ = 'bar'
    MemberDescriptorType = type(_foo.bar)
    del _foo


sn_ok = _py34
if sn_ok:
    try:
        SimpleNamespace
    except NameError:
        sn_ok = False
        __all__.append('SimpleNamespace')

if not sn_ok:
    from abc import ABCMeta
    from xoutil.eight.meta import metaclass

    from xoutil.reprlib import recursive_repr

    class SimpleNamespace(metaclass(ABCMeta)):
        '''A simple attribute-based namespace.

        SimpleNamespace(**kwargs)

        '''

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

        def __eq__(self, other):
            # TODO: This method is not implemented in py33
            ok = isinstance(other, SimpleNamespace)
            return ok and self.__dict__ == other.__dict__

        @recursive_repr(str('namespace(...)'))
        def __repr__(self):
            keys = sorted(self.__dict__)
            items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
            return "{}({})".format('namespace', ", ".join(items))

    del recursive_repr, ABCMeta, metaclass

    try:
        from types import SimpleNamespace as _sns
        # TODO: @manu, why needed in this case?
        SimpleNamespace.register(_sns)
        del _sns
    except ImportError:
        pass

try:
    DynamicClassAttribute
except NameError:
    class DynamicClassAttribute(object):
        """Route attribute access on a class to `~object.__getattr__`:meth:.

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
            _has_method = bool(getattr(fget, '__isabstractmethod__', False))
            self.__isabstractmethod__ = _has_method

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
            cls = type(self)
            result = cls(fget, self.fset, self.fdel, fdoc or self.__doc__)
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

    __all__.append('DynamicClassAttribute')

try:
    new_class
except NameError:
    from xoutil.eight._types import new_class    # noqa
    __all__.append('new_class')

try:
    prepare_class
except NameError:
    from xoutil.eight._types import prepare_class    # noqa
    __all__.append('prepare_class')

try:
    from types import _calculate_meta
except ImportError:
    from xoutil.eight._types import _calculate_meta    # noqa

del _py2, _py34
