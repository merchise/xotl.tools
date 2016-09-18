#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_metaclass
#----------------------------------------------------------------------
# Copyright (c) 2015, 2016 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-05-06

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        # unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)


try:
    from xoutil.release import VERSION_INFO
except ImportError:
    VERSION_INFO = (1, 6, 10)  # Latest release without this attribute.


def test_older_import():
    try:
        from xoutil.objects import metaclass  # noqa
    except ImportError:
        assert VERSION_INFO[:3] > (1, 7, 1), \
            'xoutil.objects.metaclass should still exists in 1.7.0'
    else:
        assert VERSION_INFO[:3] <= (1, 7, 1), \
            'xoutil.object.metaclass should be removed from 1.7.2'


def test_basic_inline_metaclass():
    from xoutil.eight.meta import metaclass

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


def test_atypical_metaclass():
    from xoutil.eight.meta import metaclass

    class API(object):
        def values(self, obj):
            def item(key):
                if key.startswith('_'):
                    return ''
                else:
                    value = getattr(obj, key)
                    if not hasattr(value, 'im_func'):
                        doc = type(value).__name__
                    elif value.__doc__ is None:
                        doc = 'no docstring'
                    else:
                        doc = value.__doc__
                return '%10s : %s' % (key, doc)
            res = [item(el) for el in dir(obj)]
            return '\n'.join([el for el in res if el != ''])

        def __get__(self, instance, klass):
            if instance is not None:
                return self.values(instance)
            else:
                return self.values(klass)

    class MyMeta(type):
        pass

    def apify(clsname, bases, attrs):
        if '__doc__' not in attrs:
            attrs['__doc__'] = API()
        return MyMeta(clsname, bases, attrs)

    class AutoAPI(metaclass(apify)):
        def foobar(self):
            pass

    assert isinstance(AutoAPI, MyMeta), 'Wrong metaclass %r' % type(AutoAPI)
    assert AutoAPI.__bases__ == (object, ), 'Invalid bases %r' % \
        AutoAPI.__bases__
    assert AutoAPI.__doc__ is not None


def test_no_double_registration_with_inlinemetaclass():
    import sys
    from xoutil.eight.meta import metaclass
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
    from xoutil.eight.meta import metaclass
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
    from xoutil.eight.meta import metaclass

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

        def __init__(self, name, bases, attrs, **kwargs):
            pass

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

        def __init__(self, name, bases, attrs, **kwargs):
            pass

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


def test_type():
    from xoutil.eight.meta import metaclass

    class x(metaclass(type)):
        pass
