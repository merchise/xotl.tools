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


'''Unnecessary implementation.

See :mod:`xoutil.eight.types`.  This implementation was there, I don't
remember why, but is not used at all and wrong.  :class:`MappingProxyType` is
named "DictProxyType" in Python 2.x.

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)


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
