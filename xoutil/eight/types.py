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


try:
    from types import DictProxyType
except ImportError:
    DictProxyType = type(object.__dict__)


from types import MemberDescriptorType, GetSetDescriptorType
if MemberDescriptorType is GetSetDescriptorType:    # As in pypy
    class _foo(object):
        __slots__ = 'bar'
    MemberDescriptorType = type(_foo.bar)
    del _foo


try:
    from types import NoneType
except ImportError:
    NoneType = type(None)


try:
    from types import MappingProxyType
except ImportError:
    from collections import MappingView, MutableMapping

    class MappingProxyType(MappingView, MutableMapping):
        def __init__(self, mapping):
            from collections import Mapping
            if not isinstance(mapping, Mapping):
                raise TypeError
            super(MappingProxyType, self).__init__(mapping)

        def items(self):
            # TODO: migrate to `xoutil.eight.collections`
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
            # TODO: migrate to `xoutil.eight.collections`
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
            # TODO: migrate to `xoutil.eight.collections`
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

    del MappingView, MutableMapping


try:
    from types import SimpleNamespace
except ImportError:
    # TODO: migrate to `xoutil.eight.reprlib`
    from xoutil.reprlib import recursive_repr

    class SimpleNamespace(object):
        '''A simple attribute-based namespace.

        SimpleNamespace(**kwargs)

        '''

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

        def __eq__(self, other):
            return self.__dict__ == other.__dict__

        @recursive_repr(str('namespace(...)'))
        def __repr__(self):
            keys = sorted(self.__dict__)
            items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
            return "{}({})".format('namespace', ", ".join(items))

    del recursive_repr


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

try:
    from types import new_class
except ImportError:
    # PEP 3115 compliant dynamic class creation.  Used in
    # xoutil.objects.metaclass
    #
    # Taken from Python 3.3 code-base.
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


try:
    from types import prepare_class
except ImportError:
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


try:
    from types import _calculate_meta
except ImportError:
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
            raise TypeError("metaclass conflict: the metaclass of a derived "
                            "class must be a (non-strict) subclass of the "
                            "metaclasses of all its bases")
        return winner
