#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#


import unittest
from xotl.tools.symbols import boolean


class BooleanTests(unittest.TestCase):
    def test_singletons(self):
        from sys import intern
        from xotl.tools.symbols import Unset

        foo = "Un"
        bar = "set"
        a = boolean("Unset")
        b = boolean(foo + "set")
        c = boolean("Un" + bar)

        # self.assertIs(intern(foo + bar), repr(Unset))
        # above started to fail in PyPy, changed to next.
        self.assertIs(intern(foo + bar), intern(repr(Unset)))
        self.assertIs(repr(a), repr(b))
        self.assertIs(a, Unset)
        self.assertIs(b, Unset)
        self.assertIs(c, Unset)

    def test_equality(self):
        a = boolean("false")
        b = boolean("true", True)
        self.assertEqual(a, False)
        self.assertEqual(b, True)
        self.assertEqual(not b, False)

    def test_parse(self):
        a = boolean("false")
        b = boolean("true", True)
        c = boolean.parse(repr(a))
        self.assertIs(boolean.parse("false"), a)
        self.assertIs(boolean.parse("true"), b)
        self.assertIs(a, c)

    def test_int_compatibility(self):
        a = boolean("false")
        b = boolean("true", True)
        self.assertEqual(a + 1, 1)
        self.assertEqual(b + 1, 2)

    def test_comments(self):
        a = boolean("false")
        value = "%s    # This is a comment" % a
        b = boolean.parse(value)
        self.assertIs(a, b)

    def test_symbols_are_pickable(self):
        import pickle
        from xotl.tools.symbols import Unset, Undefined

        for protocol in range(pickle.DEFAULT_PROTOCOL, pickle.HIGHEST_PROTOCOL + 1):
            self.assertIs(Unset, pickle.loads(pickle.dumps(Unset, protocol)))
            self.assertIs(Undefined, pickle.loads(pickle.dumps(Undefined, protocol)))


def test_symbols_is_importable():
    import sys

    modules = {
        mod: sys.modules[mod] for mod in sys.modules if mod.startswith("xotl.tools.")
    }
    for mod in modules:
        sys.modules.pop(mod)
    try:
        import xotl.tools.symbols  # noqa
    finally:
        for modname, mod in modules.items():
            sys.modules[modname] = mod
