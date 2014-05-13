#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_metaclass
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-05-06

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)


def test_basic_inline_metaclass():
    from xoutil.objects import metaclass

    class Meta(type):
        pass

    class Base(metaclass(Meta)):
        pass

    class Entity(Base):
        pass

    assert isinstance(Base, Meta), 'Wrong metaclass %r' % type(Base)
    assert isinstance(Entity, Meta), 'Wrong metaclass %r' % type(Entity)
    assert Entity.__base__ is Base
    assert Base.__base__ is object


def test_no_double_registration_with_inlinemetaclass():
    import sys
    from xoutil.objects import metaclass
    py32 = sys.version_info >= (3, 2)

    class RegisteringType(type):
        classes = []

        def __new__(cls, name, bases, attrs):
            res = super(RegisteringType, cls).__new__(cls, name, bases, attrs)
            cls.classes.append(res)
            return res

    class Base(metaclass(RegisteringType)):
        pass

    class SubType(RegisteringType):
        pass

    class Egg(metaclass(SubType), Base):
        pass

    assert len(RegisteringType.classes) == 2

    class Spam(Base, metaclass(SubType)):
        'Like "Egg" but registered twice in Python 2.x.'

    assert len(RegisteringType.classes) == (3 if py32 else 4)


def test_inlinemetaclass_decorator_with_slots():
    from xoutil.objects import metaclass
    from xoutil.types import MemberDescriptorType

    class Meta(type):
        pass

    class Base(metaclass(Meta)):
        __slots__ = 'attr'

    class Ok(metaclass(Meta)):
        def __init__(self, **kwargs):
            self.__dict__ = kwargs

        @classmethod
        def clmethod(cls):
            return cls

        @staticmethod
        def stmethod(echo):
            return echo

        def echo(self, echo):
            return self, echo

    assert isinstance(Base.attr, MemberDescriptorType)
    assert isinstance(Base, Meta), 'Wrong metaclass %r' % type(Base)
    assert isinstance(Ok, Meta), 'Wrong metaclass %r' % type(Ok)

    b = Base()
    b.attr = 1
    try:
        b.another = 2
        assert False, 'Should have raised AttributeError'
    except AttributeError:
        pass
    except:
        assert False, 'Should have raised AttributeError'

    ok = Ok(name='ok')
    assert ok.stmethod(ok) == ok
    assert ok.clmethod() == Ok
    assert ok.echo(1) == (ok, 1)
    assert ok.name == 'ok'


def test_prepare_a_class():
    import sys
    from xoutil.objects import metaclass

    class ClassDict(dict):
        pass

    class Meta(type):
        @classmethod
        def __prepare__(cls, name, bases, **kwargs):
            return ClassDict(kwargs, __prepared__=True)

        def __new__(cls, name, bases, attrs, **kwargs):
            assert isinstance(attrs, ClassDict), 'Wrong type %r' % type(attrs)
            assert attrs['__prepared__'] is True
            return super(Meta, cls).__new__(cls, name, bases, attrs)

    class AnotherClassDict(ClassDict):
        pass

    class Submeta(Meta):
        @classmethod
        def __prepare__(cls, name, bases, **kwargs):
            res = super(Submeta, cls).__prepare__(name, bases, **kwargs)
            return AnotherClassDict(res)

        def __new__(cls, name, bases, attrs, **kwargs):
            res = super(Submeta, cls).__new__(cls, name, bases, attrs,
                                              **kwargs)
            assert isinstance(attrs, AnotherClassDict)
            return res

    class SubmetaLight(Meta):
        pass

    class Foobar(metaclass(Meta, kwarg1='Foobar')):
        pass

    try:
        class Foobar2(Foobar):
            pass
    except AssertionError:
        if sys.version_info >= (3, 0):
            raise
    else:
        if sys.version_info < (3, 0):
            assert False, 'Should have raised'

    class Foobaz(metaclass(Submeta)):
        pass

    class Eggbag(metaclass(SubmetaLight)):
        pass
