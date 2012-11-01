#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_classical_aop
#----------------------------------------------------------------------
# Copyright (c) 2012 Medardo Rodríguez
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
# Created on Apr 29, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

import unittest
from xoutil.aop.classical import _weave_after_method, StopExceptionChain
from xoutil.aop.extended import weave


__docstring_format__ = 'rst'
__author__ = 'manu'




class TestClassicalAOP(unittest.TestCase):
    def setUp(self):
        class LoggerAspect(object):
            def _after_echo(self, method, result, exc_value):
                return self, result

        self.logger = LoggerAspect


    def test_after_methods_for_classmethods(self):
        class GoodClass(object):
            @classmethod
            def echo(cls, what):
                return what

        _weave_after_method(GoodClass, self.logger, 'echo')

        self.assertEqual((GoodClass, 10), GoodClass.echo(10))
        good_instance = GoodClass()
        self.assertEqual((GoodClass, 10), good_instance.echo(10))



class TestWeaving(unittest.TestCase):
    def test_whole_weaving(self):
        class Foobar(object):
            def echo(self, what):
                return what

        class Aspect(object):
            @classmethod
            def _before_weave(cls, target):
                print('Weaving {target} with {aspect}'.format(target=target.__name__, aspect=cls.__name__))

            def _before_echo(self, method):
                print('Echoing....')

            def _after_echo(self, method, result, exc):
                print('...echoed')
                if exc:
                    raise StopExceptionChain
                return result

            def injected(self, who):
                return self.echo(who)

        weave(Aspect, Foobar)
        f = Foobar()
        self.assertEquals(10, f.echo(10))



class TestWeavingModules(unittest.TestCase):
    def setUp(self):
        from xoutil.tests import testbed
        self.testbed = testbed

    def test_weaving(self):
        from xoutil.tests import testbed
        from xoutil.tests.testbed import echo

        class Dupper(object):
            def _after_echo(self, method, result, exc_value):
                if not exc_value:
                    return result * 2

        weave(Dupper, self.testbed)

        self.assertEquals(20, testbed.echo(10))
        # Unfortunally is quite difficult to replace standing references. Is
        # possible by keeping the old func_code function and replacing func_code
        # directly, but is difficult to get right and I don't need it.
        self.assertEquals(10, echo(10))



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_after_methods']
    unittest.main(verbosity=2)