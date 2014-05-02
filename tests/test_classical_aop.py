#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_classical_aop
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Manuel Vázquez Acosta
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Apr 29, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

import unittest
from xoutil.aop.classical import _weave_after_method, StopExceptionChain
from xoutil.aop.extended import weave


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


class TestExtendedWeaving(unittest.TestCase):
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
        import testbed
        self.testbed = testbed

    def test_weaving(self):
        import testbed
        from testbed import echo

        class Dupper(object):
            def _after_echo(self, method, result, exc_value):
                if not exc_value:
                    return result * 2

            def _after_rien(self, method, result, exc_value):
                return result + 1

            def _after_method(self, method, result, exc_value):
                return result

        weave(Dupper, self.testbed)

        self.assertEquals(20, testbed.echo(10))
        self.assertEquals(2, testbed.rien())
        module, args, kwargs = testbed.method(1, 2, 3, a=1)
        self.assertEquals(args, (1, 2, 3))
        self.assertEquals(kwargs, {'a': 1})
        self.assertEquals(testbed, module)

        # Unfortunately is quite difficult to replace standing references. Is
        # possible by keeping the old func_code function and replacing
        # func_code directly, but is difficult to get right and I don't need
        # it.
        self.assertEquals(10, echo(10))

        # After the test, since other may require normal echo behavior, let's
        # restore it
        testbed.echo = echo


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_after_methods']
    unittest.main(verbosity=2)
