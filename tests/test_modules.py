#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

import sys
import unittest

from xoutil.modules import customize, modulemethod


class TestModulesCustomization(unittest.TestCase):
    def setUp(self):
        import testbed
        self.testbed = testbed

    def tearDown(self):
        sys.modules[self.testbed.__name__] = self.testbed

    def test_echo(self):
        import testbed
        module, created, klass = customize(testbed)
        self.assertEqual(10, module.echo(10))

    def test_module_props(self):
        @property
        def this(mod):
            return mod

        import testbed
        attrs = {'this': this}
        module, created, klass = customize(testbed, custom_attrs=attrs)
        self.assertEqual(module, module.this)


class TestModuleDecorators(unittest.TestCase):
    def test_echo_module_level(self):
        import sys

        @modulemethod
        def echo(self, *args):
            return (self, args)

        current_module = sys.modules[__name__]
        self.assertEquals((current_module, (1, 2)), echo(1, 2))

    def test_moduleproperties(self):
        import customizetestbed as m
        self.assertIs(m, m.this)
        self.assertIs(None, m.store)
        self.assertIsNone(m.prop)
        m.store = (1, 2)
        m.prop = 'prop'
        self.assertEquals((1, 2), m.store)
        self.assertEquals((1, 2), m._store)
        self.assertIs('prop', m.prop)

        with self.assertRaises(AttributeError):
            m.this = 1

        del m.store
        with self.assertRaises(AttributeError):
            m._store == ()
        self.assertIs(None, m.store)

        del m.prop
        with self.assertRaises(AttributeError):
            m._prop == 'prop'
        self.assertIsNone(m.prop)

    def test_module_level_memoized_props(self):
        import customizetestbed as m
        from xoutil.future.inspect import getattr_static
        self.assertNotEquals(getattr_static(m, 'memoized'), m)
        self.assertIs(m.memoized, m)
        self.assertIs(getattr_static(m, 'memoized'), m)


def test_get_module_path_by_module_object():
    import xoutil
    import xoutil.iterators
    from os.path import join
    from xoutil.modules import get_module_path
    top = xoutil.__path__[0]
    expected = top
    assert get_module_path(xoutil) == expected

    expected = (join(top, 'iterators.py'),
                join(top, 'iterators.pyc'),
                join(top, 'iterators.pyo'))
    assert get_module_path(xoutil.iterators) in expected


def test_get_module_path_by_module_string_abs():
    import xoutil
    from os.path import join
    from xoutil.modules import get_module_path
    top = xoutil.__path__[0]
    expected = top
    assert get_module_path('xoutil') == expected
    expected = (join(top, 'iterators.py'),
                join(top, 'iterators.pyc'),
                join(top, 'iterators.pyo'))
    assert get_module_path('xoutil.iterators') in expected


def test_get_module_path_by_module_string_rel():
    import pytest
    from xoutil.modules import get_module_path
    with pytest.raises(TypeError):
        assert get_module_path('.iterators')


def test_object_stability():
    import testbed
    from testbed import selfish
    a, b = testbed.selfish()
    c, d = selfish()
    e, f = testbed.selfish()
    assert a == c == e
    assert b == d == f
