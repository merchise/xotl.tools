#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Some functions implemented in module ``types`` in Python 3 but not in
Python 2 needed for '_meta*' implementation.

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)


__all__ = ['new_class', 'prepare_class', '_calculate_meta', 'get_exec_body']


try:
    from types import new_class
except ImportError:
    # Provide a PEP 3115 compliant mechanism for class creation.  Used in
    # xoutil.eight.meta.metaclass
    #
    # Taken from Python 3.3 code-base.
    def new_class(name, bases=(), kwds=None, exec_body=None):
        """Create a class object dynamically using the appropriate metaclass.

        """
        meta, ns, kwds = prepare_class(name, bases, kwds)
        if exec_body is not None:
            exec_body(ns)
        return meta(name, bases, ns, **kwds)

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
        from xoutil.eight import typeof
        if kwds is None:
            kwds = {}
        else:
            kwds = dict(kwds)  # Don't alter the provided mapping
        meta = kwds.pop('metaclass', None)
        if not meta:
            meta = typeof(bases[0]) if bases else type
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
    # XXX: Remove all these `continue` statements
    def _calculate_meta(meta, bases):
        """Calculate the most derived metaclass."""
        from xoutil.eight import typeof, class_types
        old_cls = next((cls for cls in class_types if cls is not type), None)
        winner = meta
        for base in bases:
            base_meta = typeof(base)
            if issubclass(winner, base_meta):
                continue  # noqa
            if issubclass(base_meta, winner):
                winner = base_meta
                continue  # noqa
            # else:
            raise TypeError("metaclass conflict: the metaclass of a derived "
                            "class must be a (non-strict) subclass of the "
                            "metaclasses of all its bases")
        if winner is not old_cls:
            return winner
        else:
            msg = ("Error when calling the metaclass bases\n\t"
                   "a new-style class can't have only classic bases")
            raise TypeError(msg)


try:
    from types import MappingProxyType
except ImportError:
    from collections import Mapping

    class mappingproxy(Mapping):
        '''Python 3 compatible implementation for Python 2 'DictProxyType'.

        `DictProxyType`:class: can't be used as a simple alias because there
        are some Python 3 code that create instances.

        '''
        __slots__ = ('_mapping',)

        def __init__(self, mapping):
            from xoutil.eight import type_name as tname
            from xoutil.future.collections import Mapping
            if isinstance(mapping, Mapping):
                self._mapping = mapping
            else:
                msg = '{}() argument must be a mapping, not {}'
                raise TypeError(msg.format(tname(self), tname(mapping)))

        def __len__(self):
            return len(self._mapping)

        def __str__(self):
            return str(dict(self))

        def __repr__(self):
            return '{0.__class__.__name__}({0._mapping!r})'.format(self)

        def items(self):
            from xoutil.future.collections import ItemsView
            try:
                items = type(self._mapping).__dict__['items']
                if items is not dict.__dict__['items']:
                    return items(self._mapping)
                else:
                    return ItemsView(self)
            except KeyError:
                return ItemsView(self)

        def keys(self):
            from xoutil.future.collections import KeysView
            try:
                keys = type(self._mapping).__dict__['keys']
                if keys is not dict.__dict__['keys']:
                    return keys(self._mapping)
                else:
                    return KeysView(self)
            except KeyError:
                return KeysView(self)

        def values(self):
            from xoutil.future.collections import ValuesView
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

        def __getitem__(self, key):
            return self._mapping[key]

        def __dir__(self):
            return dir(type(type.__dict__))

    MappingProxyType = mappingproxy


def get_exec_body(**kwargs):
    '''Return an `exec_body` function that update `ns` with `kwargs`.'''
    def exec_body(ns):
        ns.update(kwargs)
        return ns
    return exec_body
