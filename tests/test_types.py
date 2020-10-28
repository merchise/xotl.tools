#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import unittest
import pickle
import sys

from xotl.tools.future import types


def test_iscollection():
    # TODO: move this test to equivalent for
    # `xotl.tools.values.simple.logic_collection_coerce`
    from xotl.tools.future.collections import UserList, UserDict

    def is_collection(arg):
        from collections.abc import Iterable, Mapping

        avoid = (Mapping, str)
        return isinstance(arg, Iterable) and not isinstance(arg, avoid)

    assert is_collection("all strings are iterable") is False
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


class NoneTypeTests(unittest.TestCase):
    "To avoid FlyCheck errors"

    def test_identity(self):
        from xotl.tools.future.types import NoneType

        self.assertIs(NoneType, type(None))


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
        self.assertEqual(vars(ns2), {"y": 2, "x": 1})
        self.assertEqual(len(ns3.__dict__), 2)
        self.assertEqual(vars(ns3), {"y": 2, "x": 1})

    def test_unbound(self):
        ns1 = vars(types.SimpleNamespace())
        ns2 = vars(types.SimpleNamespace(x=1, y=2))

        self.assertEqual(ns1, {})
        self.assertEqual(ns2, {"y": 2, "x": 1})

    def test_underlying_dict(self):
        ns1 = types.SimpleNamespace()
        ns2 = types.SimpleNamespace(x=1, y=2)
        ns3 = types.SimpleNamespace(a=True, b=False)
        mapping = ns3.__dict__
        del ns3

        self.assertEqual(ns1.__dict__, {})
        self.assertEqual(ns2.__dict__, {"y": 2, "x": 1})
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
        ns1.a = "spam"
        ns1.b = "ham"
        ns2.z = 4
        ns2.theta = None

        self.assertEqual(ns1.__dict__, dict(a="spam", b="ham"))
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
        ns2.y = "spam"
        self.assertEqual(vars(ns2), dict(w=3, x=1, y="spam"))
        del ns2.y
        self.assertEqual(vars(ns2), dict(w=3, x=1))

        ns1.spam = 5
        self.assertEqual(vars(ns1), dict(spam=5))
        del ns1.spam
        self.assertEqual(vars(ns1), {})

    @unittest.skipIf(sys.version_info >= (3, 9), "Different order in Python 3.9")
    def test_repr(self):
        ns1 = types.SimpleNamespace(x=1, y=2, w=3)
        ns2 = types.SimpleNamespace()
        ns2.x = str("spam")
        ns2._y = 5
        name = "namespace"

        self.assertEqual(repr(ns1), "{name}(w=3, x=1, y=2)".format(name=name))
        self.assertEqual(repr(ns2), "{name}(_y=5, x='spam')".format(name=name))

    @unittest.skipIf(sys.version_info < (3, 9), "Different order in Python 3.9")
    def test_repr_py39(self):
        ns1 = types.SimpleNamespace(x=1, y=2, w=3)
        ns2 = types.SimpleNamespace()
        ns2.x = str("spam")
        ns2._y = 5
        name = "namespace"

        self.assertEqual(repr(ns1), "{name}(x=1, y=2, w=3)".format(name=name))
        self.assertEqual(repr(ns2), "{name}(x='spam', _y=5)".format(name=name))

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
        ns2.ham = "?"
        ns2.spam = ns3

        self.assertEqual(vars(ns1), dict(a=1, b=2))
        self.assertEqual(vars(ns2), dict(spam=ns3, ham="?"))
        self.assertEqual(ns2.spam, ns3)
        self.assertEqual(vars(ns3), dict(x=ns1))
        self.assertEqual(ns3.x.a, 1)

    def test_recursive(self):
        ns1 = types.SimpleNamespace(c="cookie")
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

    @unittest.skipIf(sys.version_info >= (3, 9), "Different order in Python 3.9")
    def test_recursive_repr(self):
        ns1 = types.SimpleNamespace(c=str("cookie"))
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

    @unittest.skipIf(sys.version_info < (3, 9), "Different order in Python 3.9")
    def test_recursive_repr_py39(self):
        ns1 = types.SimpleNamespace(c=str("cookie"))
        ns2 = types.SimpleNamespace()
        ns3 = types.SimpleNamespace(x=1)
        ns1.spam = ns1
        ns2.spam = ns3
        ns3.spam = ns2
        name = "namespace"
        repr1 = "{name}(c='cookie', spam={name}(...))".format(name=name)
        repr2 = "{name}(spam={name}(x=1, spam={name}(...)))".format(name=name)

        self.assertEqual(repr(ns1), repr1)
        self.assertEqual(repr(ns2), repr2)

    def test_as_dict(self):
        ns = types.SimpleNamespace(spam="spamspamspam")

        with self.assertRaises(TypeError):
            len(ns)
        with self.assertRaises(TypeError):
            iter(ns)
        with self.assertRaises(TypeError):
            "spam" in ns
        with self.assertRaises(TypeError):
            ns["spam"]

    def test_subclass(self):
        class Spam(types.SimpleNamespace):
            pass

        spam = Spam(ham=8, eggs=9)

        self.assertIs(type(spam), Spam)
        self.assertEqual(vars(spam), {"ham": 8, "eggs": 9})

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
        from xotl.tools.future.types import DynamicClassAttribute  # noqa
