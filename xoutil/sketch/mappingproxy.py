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


# TODO: Next tests failed in py27 and pypy configurations (not in py34).  I
# don't understand why we must create instances from `MappingProxyType`.  If a
# clone of a dictionary is needed, ``.copy`` method must be used. [manu]
# remove all this tests class or explain why this is necessary.
class MappingProxyTests(unittest.TestCase):
    mappingproxy = xoutil.types.MappingProxyType

    def test_constructor(self):
        class userdict(dict):
            pass

        mapping = {'x': 1, 'y': 2}
        self.assertEqual(self.mappingproxy(mapping), mapping)
        mapping = userdict(x=1, y=2)
        self.assertEqual(self.mappingproxy(mapping), mapping)
        mapping = collections.ChainMap({'x': 1}, {'y': 2})
        self.assertEqual(self.mappingproxy(mapping), mapping)

        self.assertRaises(TypeError, self.mappingproxy, 10)
        self.assertRaises(TypeError, self.mappingproxy, ("a", "tuple"))
        self.assertRaises(TypeError, self.mappingproxy, ["a", "list"])

    def test_methods(self):
        attrs = set(dir(self.mappingproxy({}))) - set(dir(object()))
        self.assertEqual(attrs, {
            '__contains__',
            '__getitem__',
            '__iter__',
            '__len__',
            'copy',
            'get',
            'items',
            'keys',
            'values',
        })

    def test_get(self):
        view = self.mappingproxy({'a': 'A', 'b': 'B'})
        self.assertEqual(view['a'], 'A')
        self.assertEqual(view['b'], 'B')
        self.assertRaises(KeyError, view.__getitem__, 'xxx')
        self.assertEqual(view.get('a'), 'A')
        self.assertIsNone(view.get('xxx'))
        self.assertEqual(view.get('xxx', 42), 42)

    def test_missing(self):
        class dictmissing(dict):
            def __missing__(self, key):
                return "missing=%s" % key

        view = self.mappingproxy(dictmissing(x=1))
        self.assertEqual(view['x'], 1)
        self.assertEqual(view['y'], 'missing=y')
        self.assertEqual(view.get('x'), 1)
        self.assertEqual(view.get('y'), None)
        self.assertEqual(view.get('y', 42), 42)
        self.assertTrue('x' in view)
        self.assertFalse('y' in view)

    def test_customdict(self):
        class customdict(dict):
            def __contains__(self, key):
                if key == 'magic':
                    return True
                else:
                    return dict.__contains__(self, key)

            def __iter__(self):
                return iter(('iter',))

            def __len__(self):
                return 500

            def copy(self):
                return 'copy'

            def keys(self):
                return 'keys'

            def items(self):
                return 'items'

            def values(self):
                return 'values'

            def __getitem__(self, key):
                return "getitem=%s" % dict.__getitem__(self, key)

            def get(self, key, default=None):
                return "get=%s" % dict.get(self, key, 'default=%r' % default)

        custom = customdict({'key': 'value'})
        view = self.mappingproxy(custom)
        self.assertTrue('key' in view)
        self.assertTrue('magic' in view)
        self.assertFalse('xxx' in view)
        self.assertEqual(view['key'], 'getitem=value')
        self.assertRaises(KeyError, view.__getitem__, 'xxx')
        self.assertEqual(tuple(view), ('iter',))
        self.assertEqual(len(view), 500)
        self.assertEqual(view.copy(), 'copy')
        self.assertEqual(view.get('key'), 'get=value')
        self.assertEqual(view.get('xxx'), 'get=default=None')
        self.assertEqual(view.items(), 'items')
        self.assertEqual(view.keys(), 'keys')
        self.assertEqual(view.values(), 'values')

    def test_chainmap(self):
        d1 = {'x': 1}
        d2 = {'y': 2}
        mapping = collections.ChainMap(d1, d2)
        view = self.mappingproxy(mapping)
        self.assertTrue('x' in view)
        self.assertTrue('y' in view)
        self.assertFalse('z' in view)
        self.assertEqual(view['x'], 1)
        self.assertEqual(view['y'], 2)
        self.assertRaises(KeyError, view.__getitem__, 'z')
        self.assertEqual(tuple(sorted(view)), ('x', 'y'))
        self.assertEqual(len(view), 2)
        copy = view.copy()
        self.assertIsNot(copy, mapping)
        self.assertTrue(isinstance(copy, collections.ChainMap))
        self.assertEqual(copy, mapping)
        self.assertEqual(view.get('x'), 1)
        self.assertEqual(view.get('y'), 2)
        self.assertIsNone(view.get('z'))
        self.assertEqual(tuple(sorted(view.items())), (('x', 1), ('y', 2)))
        self.assertEqual(tuple(sorted(view.keys())), ('x', 'y'))
        self.assertEqual(tuple(sorted(view.values())), (1, 2))

    def test_contains(self):
        view = self.mappingproxy(dict.fromkeys('abc'))
        self.assertTrue('a' in view)
        self.assertTrue('b' in view)
        self.assertTrue('c' in view)
        self.assertFalse('xxx' in view)

    def test_views(self):
        mapping = {}
        view = self.mappingproxy(mapping)
        keys = view.keys()
        values = view.values()
        items = view.items()
        self.assertEqual(list(keys), [])
        self.assertEqual(list(values), [])
        self.assertEqual(list(items), [])
        mapping['key'] = 'value'
        self.assertEqual(list(keys), ['key'])
        self.assertEqual(list(values), ['value'])
        self.assertEqual(list(items), [('key', 'value')])

    def test_len(self):
        for expected in range(6):
            data = dict.fromkeys('abcde'[:expected])
            self.assertEqual(len(data), expected)
            view = self.mappingproxy(data)
            self.assertEqual(len(view), expected)

    def test_iterators(self):
        keys = ('x', 'y')
        values = (1, 2)
        items = tuple(zip(keys, values))
        view = self.mappingproxy(dict(items))
        self.assertEqual(set(view), set(keys))
        self.assertEqual(set(view.keys()), set(keys))
        self.assertEqual(set(view.values()), set(values))
        self.assertEqual(set(view.items()), set(items))

    def test_copy(self):
        original = {'key1': 27, 'key2': 51, 'key3': 93}
        view = self.mappingproxy(original)
        copy = view.copy()
        self.assertEqual(type(copy), dict)
        self.assertEqual(copy, original)
        original['key1'] = 70
        self.assertEqual(view['key1'], 70)
        self.assertEqual(copy['key1'], 27)
