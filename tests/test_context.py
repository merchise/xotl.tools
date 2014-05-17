#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.test_context
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-01-15

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

import unittest
from xoutil.context import context


class TestContext(unittest.TestCase):
    def test_simple_contexts(self):
        with context('CONTEXT-1'):
            self.assertIsNot(None, context['CONTEXT-1'])
            with context('CONTEXT-1'):
                with context('context-2'):
                    self.assertIsNot(None, context['CONTEXT-1'])
                    self.assertIsNot(None, context['context-2'])
                self.assertEquals(False, bool(context['context-2']))
            self.assertIsNot(None, context['CONTEXT-1'])
        self.assertEquals(False, bool(context['CONTEXT-1']))

    def test_with_objects(self):
        CONTEXT1 = object()
        CONTEXT2 = object()
        with context(CONTEXT1):
            self.assertIsNot(None, context[CONTEXT1])
            with context(CONTEXT1):
                with context(CONTEXT2):
                    self.assertIsNot(None, context[CONTEXT1])
                    self.assertIsNot(None, context[CONTEXT2])
                self.assertEquals(False, bool(context[CONTEXT2]))
            self.assertIsNot(None, context[CONTEXT1])
        self.assertEquals(False, bool(context[CONTEXT1]))


def test_stacking_of_data_does_not_leak():
    c1 = 'CONTEXT-1'
    with context(c1, a=1, b=1) as cc1:
        assert cc1['a'] == 1
        with context(c1, a=2, z='zzz') as cc2:
            assert cc2 is cc1
            assert cc2['a'] == 2
            assert cc2['b'] == 1   # Given by the upper enclosing level
            assert cc2['z'] == 'zzz'

            # Let's change it for this level
            cc2['b'] = 'jailed!'
            assert cc2['b'] == 'jailed!'

        # But in the upper level both a and b stay the same
        assert cc1['a'] == 1
        assert cc1['b'] == 1
        assert set(cc1) == {'a', 'b'}

    try:
        assert cc1['a'] == 1
        assert False
    except (IndexError, KeyError):
        pass


def test_data_is_an_opendict():
    c1 = object()
    with context(c1, a=1, b=1) as cc1:
        with context(c1, a=2) as cc2:
            assert cc2 is cc1
            assert cc2.a == 2
            assert cc2.b == 1   # Given by the upper enclosing level
            cc2.b = 'jaile!d'
        assert cc1.a == 1
        assert cc1['b'] == 1


def test_reusing_raises():
    with context('a') as a:
        try:
            with a:
                pass
            assert False, 'It should have raised a RuntimeError'
        except RuntimeError:
            pass
        except:
            assert False, 'It should have raised a RuntimeError'
