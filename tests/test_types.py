#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_types
#----------------------------------------------------------------------
# Copyright (c) 2012, 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-11-25

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

import unittest
import pickle

import xoutil.types
from xoutil import types
from xoutil import collections


def test_NoneType_exists():
    from xoutil.types import NoneType
    assert NoneType is type(None)


def test_iscollection():
    from xoutil.types import is_collection
    from xoutil.six.moves import range
    from xoutil.collections import UserList, UserDict
    assert is_collection('all strings are iterable') is False
    assert is_collection(1) is False
    assert is_collection(range(1)) is True
    assert is_collection({}) is False
    assert is_collection(tuple()) is True
    assert is_collection(set()) is True
    assert is_collection(a for a in range(100)) is True

    class Foobar(UserList):
        pass

    assert is_collection(Foobar()) is True

    class Foobar(UserDict):
        pass

    assert is_collection(Foobar()) is False


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


class SimpleNamespaceTests(unittest.TestCase):

    def test_constructor(self):
        ns1 = types.SimpleNamespace()
        ns2 = types.SimpleNamespace(x=1, y=2)
        ns3 = types.SimpleNamespace(**dict(x=1, y=2))

        with self.assertRaises(TypeError):
            types.SimpleNamespace(1, 2, 3)

        self.assertEqual(len(ns1.__dict__), 0)
        self.assertEqual(vars(ns1), {})
        self.assertEqual(len(ns2.__dict__), 2)
        self.assertEqual(vars(ns2), {'y': 2, 'x': 1})
        self.assertEqual(len(ns3.__dict__), 2)
        self.assertEqual(vars(ns3), {'y': 2, 'x': 1})

    def test_unbound(self):
        ns1 = vars(types.SimpleNamespace())
        ns2 = vars(types.SimpleNamespace(x=1, y=2))

        self.assertEqual(ns1, {})
        self.assertEqual(ns2, {'y': 2, 'x': 1})

    def test_underlying_dict(self):
        ns1 = types.SimpleNamespace()
        ns2 = types.SimpleNamespace(x=1, y=2)
        ns3 = types.SimpleNamespace(a=True, b=False)
        mapping = ns3.__dict__
        del ns3

        self.assertEqual(ns1.__dict__, {})
        self.assertEqual(ns2.__dict__, {'y': 2, 'x': 1})
        self.assertEqual(mapping, dict(a=True, b=False))

    def test_attrget(self):
        ns = types.SimpleNamespace(x=1, y=2, w=3)

        self.assertEqual(ns.x, 1)
        self.assertEqual(ns.y, 2)
        self.assertEqual(ns.w, 3)
        with self.assertRaises(AttributeError):
            ns.z

    def test_attrset(self):
        ns1 = types.SimpleNamespace()
        ns2 = types.SimpleNamespace(x=1, y=2, w=3)
        ns1.a = 'spam'
        ns1.b = 'ham'
        ns2.z = 4
        ns2.theta = None

        self.assertEqual(ns1.__dict__, dict(a='spam', b='ham'))
        self.assertEqual(ns2.__dict__, dict(x=1, y=2, w=3, z=4, theta=None))

    def test_attrdel(self):
        ns1 = types.SimpleNamespace()
        ns2 = types.SimpleNamespace(x=1, y=2, w=3)

        with self.assertRaises(AttributeError):
            del ns1.spam
        with self.assertRaises(AttributeError):
            del ns2.spam

        del ns2.y
        self.assertEqual(vars(ns2), dict(w=3, x=1))
        ns2.y = 'spam'
        self.assertEqual(vars(ns2), dict(w=3, x=1, y='spam'))
        del ns2.y
        self.assertEqual(vars(ns2), dict(w=3, x=1))

        ns1.spam = 5
        self.assertEqual(vars(ns1), dict(spam=5))
        del ns1.spam
        self.assertEqual(vars(ns1), {})

    def test_repr(self):
        ns1 = types.SimpleNamespace(x=1, y=2, w=3)
        ns2 = types.SimpleNamespace()
        ns2.x = str("spam")
        ns2._y = 5
        name = "namespace"

        self.assertEqual(repr(ns1), "{name}(w=3, x=1, y=2)".format(name=name))
        self.assertEqual(repr(ns2), "{name}(_y=5, x='spam')".format(name=name))

    def test_equal(self):
        ns1 = types.SimpleNamespace(x=1)
        ns2 = types.SimpleNamespace()
        ns2.x = 1

        self.assertEqual(types.SimpleNamespace(), types.SimpleNamespace())
        self.assertEqual(ns1, ns2)
        self.assertNotEqual(ns2, types.SimpleNamespace())

    def test_nested(self):
        ns1 = types.SimpleNamespace(a=1, b=2)
        ns2 = types.SimpleNamespace()
        ns3 = types.SimpleNamespace(x=ns1)
        ns2.spam = ns1
        ns2.ham = '?'
        ns2.spam = ns3

        self.assertEqual(vars(ns1), dict(a=1, b=2))
        self.assertEqual(vars(ns2), dict(spam=ns3, ham='?'))
        self.assertEqual(ns2.spam, ns3)
        self.assertEqual(vars(ns3), dict(x=ns1))
        self.assertEqual(ns3.x.a, 1)

    def test_recursive(self):
        ns1 = types.SimpleNamespace(c='cookie')
        ns2 = types.SimpleNamespace()
        ns3 = types.SimpleNamespace(x=1)
        ns1.spam = ns1
        ns2.spam = ns3
        ns3.spam = ns2

        self.assertEqual(ns1.spam, ns1)
        self.assertEqual(ns1.spam.spam, ns1)
        self.assertEqual(ns1.spam.spam, ns1.spam)
        self.assertEqual(ns2.spam, ns3)
        self.assertEqual(ns3.spam, ns2)
        self.assertEqual(ns2.spam.spam, ns2)

    def test_recursive_repr(self):
        ns1 = types.SimpleNamespace(c=str('cookie'))
        ns2 = types.SimpleNamespace()
        ns3 = types.SimpleNamespace(x=1)
        ns1.spam = ns1
        ns2.spam = ns3
        ns3.spam = ns2
        name = "namespace"
        repr1 = "{name}(c='cookie', spam={name}(...))".format(name=name)
        repr2 = "{name}(spam={name}(spam={name}(...), x=1))".format(name=name)

        self.assertEqual(repr(ns1), repr1)
        self.assertEqual(repr(ns2), repr2)

    def test_as_dict(self):
        ns = types.SimpleNamespace(spam='spamspamspam')

        with self.assertRaises(TypeError):
            len(ns)
        with self.assertRaises(TypeError):
            iter(ns)
        with self.assertRaises(TypeError):
            'spam' in ns
        with self.assertRaises(TypeError):
            ns['spam']

    def test_subclass(self):
        class Spam(types.SimpleNamespace):
            pass

        spam = Spam(ham=8, eggs=9)

        self.assertIs(type(spam), Spam)
        self.assertEqual(vars(spam), {'ham': 8, 'eggs': 9})

    def test_pickle(self):
        ns = types.SimpleNamespace(breakfast="spam", lunch="spam")

        for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
            pname = "protocol {}".format(protocol)
            try:
                ns_pickled = pickle.dumps(ns, protocol)
            except TypeError:
                raise TypeError(pname)
            ns_roundtrip = pickle.loads(ns_pickled)

            self.assertEqual(ns, ns_roundtrip, pname)


class TestDynamicClassAttribute(unittest.TestCase):
    def test_isimportable(self):
        from xoutil.types import DynamicClassAttribute
