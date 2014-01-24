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

__author__ = "Manuel Vázquez Acosta <mva.led@gmail.com>"
__date__ = "Mon May  6 15:55:00 2013"


def test_basic_inline_metaclass():
    from xoutil.objects import metaclass

    class Meta(type):
        pass

    class Base(metaclass(Meta)):
        pass

    class Entity(Base):
        pass

    assert type(Base) is Meta
    assert type(Entity) is Meta
    assert Entity.__base__ is Base
    assert Base.__base__ is object


def test_no_double_registration_with_inlinemetaclass():
    from xoutil.objects import metaclass
    from xoutil.compat import py3k

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

    assert len(RegisteringType.classes) == (3 if py3k else 4)


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
    assert isinstance(Base, Meta)
    assert isinstance(Ok, Meta)

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
