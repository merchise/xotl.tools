#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import sys
import unittest

from xotl.tools.modules import customize, modulemethod


class TestModulesCustomization(unittest.TestCase):
    def setUp(self):
        from . import testbed

        self.testbed = testbed

    def tearDown(self):
        sys.modules[self.testbed.__name__] = self.testbed

    def test_echo(self):
        from . import testbed

        module, _created, _klass = customize(testbed)
        self.assertEqual(10, module.echo(10))

    def test_module_props(self):
        @property
        def this(mod):
            return mod

        from . import testbed

        attrs = {"this": this}
        module, _created, _klass = customize(testbed, custom_attrs=attrs)
        self.assertEqual(module, module.this)


class TestModuleDecorators(unittest.TestCase):
    def test_echo_module_level(self):
        import sys

        @modulemethod
        def echo(self, *args):
            return (self, args)

        current_module = sys.modules[__name__]
        self.assertEqual((current_module, (1, 2)), echo(1, 2))

    def test_moduleproperties(self):
        from . import customizetestbed as m

        self.assertIs(m, m.this)
        self.assertIs(None, m.store)
        self.assertIsNone(m.prop)
        m.store = (1, 2)
        m.prop = "prop"
        self.assertEqual((1, 2), m.store)
        self.assertEqual((1, 2), m._store)
        self.assertIs("prop", m.prop)

        with self.assertRaises(AttributeError):
            m.this = 1

        del m.store
        with self.assertRaises(AttributeError):
            m._store == ()
        self.assertIs(None, m.store)

        del m.prop
        with self.assertRaises(AttributeError):
            m._prop == "prop"
        self.assertIsNone(m.prop)

    def test_module_level_memoized_props(self):
        from xotl.tools.future.inspect import getattr_static

        from . import customizetestbed as m

        self.assertNotEqual(getattr_static(m, "memoized"), m)
        self.assertIs(m.memoized, m)
        self.assertIs(getattr_static(m, "memoized"), m)


def test_object_stability():
    from . import testbed
    from .testbed import selfish

    a, b = testbed.selfish()
    c, d = selfish()
    e, f = testbed.selfish()
    assert a == c == e
    assert b == d == f
