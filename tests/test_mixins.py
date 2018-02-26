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


from xoutil.eight.abc import ABCMeta, ABC
from xoutil.eight.mixins import mixin, Mixin


def _get_test_classes():
    '''Return "One, Two, OneMeta, TwoMeta, Test" classes.'''
    class One(dict):
        one = 1

        def test_one(self):
            return self.one

    class Two:
        two = 2

        def test_two(self):
            return self.two

    class OneMeta(type):
        def test_one_meta(self):
            return self.one

    class TwoMeta(type):
        def test_two_meta(self):
            return self.two

    Test = mixin(One, Two, meta=[OneMeta, TwoMeta], name='Test')
    return One, Two, OneMeta, TwoMeta, Test


def test_mixins():
    One, Two, OneMeta, TwoMeta, Test = _get_test_classes()

    # Several bases and several meta-classes
    assert Test.__name__ == 'Test'
    assert Test.__bases__ == (One, Two, Mixin)
    assert Test.test_one_meta() == 1
    assert Test.test_two_meta() == 2
    assert issubclass(Test, Mixin)
    assert isinstance(Test, OneMeta)
    assert isinstance(Test, TwoMeta)
    obj = Test(one='1')
    assert obj.test_one() == 1
    assert obj.test_two() == 2
    assert obj['one'] == '1'

    # Bases canonization and generated name
    Test = mixin(object, One, dict, Two, ABC)
    assert Test.__name__ == 'OneMixin'
    assert Test.__bases__ == (One, Two, Mixin)
    assert isinstance(Test, ABCMeta)
    assert Test.register(int) is int
    assert isinstance(1, Test)

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
