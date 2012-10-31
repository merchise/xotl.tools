#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_context
#----------------------------------------------------------------------
# Copyright (c) 2012 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on Oct 30, 2012


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)

from zope.interface import Interface, implementer

from xoutil.context import context

__docstring_format__ = 'rst'
__author__ = 'manu'

import unittest


class TestInterfacedContexts(unittest.TestCase):
    def test_interfaces(self):
        class IFoo(Interface):
            pass

        class IBar(IFoo):
            pass

        @implementer(IFoo)
        class Foo(object):
            pass

        @implementer(IBar)
        class Bar(object):
            pass

        foo = Foo()
        bar = Bar()

        with context(foo) as ctx_foo:
            self.assertFalse(context[IBar])
            self.assertTrue(context[IFoo])
            with context(bar) as ctx_bar:
                self.assertIs(context[IFoo], context[IBar])
                self.assertIs(ctx_bar, context[IFoo])
                self.assertIsNot(ctx_foo, ctx_bar)
            self.assertIs(ctx_foo, context[IFoo])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(verbosity=2)