#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_mixins
#----------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2015-10-23

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)


from xoutil.eight.abc import ABCMeta, ABC
from xoutil.eight.mixins import mixin, Mixin


def test_mixins():
    class One(dict):
        one = 1

        def test_one(self):
            return self.one

    class Two(object):
        two = 2

        def test_two(self):
            return self.two

    class OneMeta(type):
        def test_one_meta(self):
            return self.one

    class TwoMeta(type):
        def test_two_meta(self):
            return self.two

    # Several bases and several meta-classes
    Test = mixin(One, Two, meta=[OneMeta, TwoMeta, ABCMeta], name='Test1')
    assert Test.__name__ == 'Test1'
    assert Test.__bases__ == (One, Two, Mixin)
    assert Test.test_one_meta() == 1
    assert Test.test_two_meta() == 2
    assert issubclass(Test, Mixin)
    assert isinstance(Test, OneMeta)
    assert isinstance(Test, TwoMeta)
    assert isinstance(Test, ABCMeta)
    obj = Test(one='1')
    assert obj.test_one() == 1
    assert obj.test_two() == 2
    assert obj['one'] == '1'
    assert Test.register(int) is int
    assert isinstance(1, Test)

    # Bases canonization and generated name
    Test = mixin(object, One, dict, Two, ABC)
    assert Test.__name__ == 'OneMixin'
    assert Test.__bases__ == (One, Two, Mixin)
    assert isinstance(Test, ABCMeta)

    # No bases or no meta-classes
    Test = mixin()
    assert Test.__name__ == 'BasicMixin'
    assert Test.__bases__ == (Mixin, )
    Test = mixin(metaclass=ABCMeta)
    assert Test.__name__ == 'BasicMixin'
    assert Test.__bases__ == (Mixin, )
    assert isinstance(Test, ABCMeta)
    Test = mixin(metaclass=ABCMeta)
    assert Test.__name__ == 'BasicMixin'
    assert Test.__bases__ == (Mixin, )
    assert type(Test) == ABCMeta
    Test = mixin(One)
    assert Test.__name__ == 'OneMixin'
    assert Test.__bases__ == (One, Mixin)
    assert type(Test) == type

    # Class attributes
    Test = mixin(One, Two, metaclass=OneMeta, name='Test', one='1')
    assert Test.__name__ == 'Test'
    assert Test.__bases__ == (One, Two, Mixin)
    assert Test.test_one_meta() == '1'
    assert Test.one == '1'
    obj = Test()
    assert obj.test_one() == '1'
    assert obj.test_two() == 2

    # Module
    Test = mixin(One, metaclass=OneMeta, name='Test', module=True)
    assert Test.__module__ == __name__
    Test = mixin(One, name='Test', module='<mixin>')
    assert Test.__module__ == '<mixin>'
    Test = mixin(One, metaclass=OneMeta, name='Test', module='<-{}->')
    assert Test.__module__ == '<-{}->'.format(__name__)

    # Name and doc as positional arguments
    doc = 'This is a test'
    Test = mixin('TestPos', doc, One)
    assert Test.__name__ == 'TestPos'
    assert doc in Test.__doc__

    # Real Mixin
    class Foobar(One, mixin(Two, meta=[TwoMeta, ABCMeta])):
        pass
    assert issubclass(Foobar, Mixin)
