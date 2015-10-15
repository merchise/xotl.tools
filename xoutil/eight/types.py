# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight.types
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-02-25


'''All functions implemented in module ``types`` in Python 3 but not in
Python 2.

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)


__all__ = [str(name) for name in ('DictProxyType', 'MemberDescriptorType',
                                  'NoneType', 'MappingProxyType',
                                  'SimpleNamespace', 'DynamicClassAttribute',
                                  'new_class', 'prepare_class', )]


import sys
_py34 = sys.version_info >= (3, 4, 0)
del sys


from types import MemberDescriptorType, GetSetDescriptorType
if MemberDescriptorType is GetSetDescriptorType:    # As in pypy
    class _foo(object):
        __slots__ = 'bar'
    MemberDescriptorType = type(_foo.bar)
    del _foo


from ._types import new_class, prepare_class, _calculate_meta    # noqa


try:
    from types import NoneType
except ImportError:
    NoneType = type(None)


try:
    from types import DictProxyType
except ImportError:
    DictProxyType = type(object.__dict__)


try:
    from types import MappingProxyType
except ImportError:
    MappingProxyType = DictProxyType

# TODO: "MappingProxyType"" is named "DictProxyType" in Python 2.x.  Deprecate
# "DictProxyType" in favor of "MappingProxyType".


if _py34:
    from types import SimpleNamespace
else:
    # TODO: migrate to `xoutil.eight.reprlib`
    from abc import ABCMeta
    from .meta import metaclass

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
        SimpleNamespace.register(_sns)
        del _sns
    except ImportError:
        pass


try:
    from types import DynamicClassAttribute
except ImportError:
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
