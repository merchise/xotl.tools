#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# tests.test_objects
# ---------------------------------------------------------------------
# Copyright (c) 2013, 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-04-16

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

import pytest
from xoutil.objects import smart_copy


def test_smart_copy():
    class new(object):
        def __init__(self, **kw):
            for k, v in kw.items():
                setattr(self, k, v)

    source = new(a=1, b=2, c=4, _d=5)
    target = {}
    smart_copy(source, target, defaults=False)
    assert target == dict(a=1, b=2, c=4)

    source = new(a=1, b=2, c=4, _d=5)
    target = {}
    smart_copy(source, target, defaults=None)
    assert target == dict(a=1, b=2, c=4)

    target = {}
    smart_copy(source, target, defaults=True)
    assert target['_d'] == 5


def test_smart_copy_with_defaults():
    defaults = {'host': 'localhost', 'port': 5432, 'user': 'openerp',
                'password': (KeyError, '{key}')}
    kwargs = {'password': 'keep-out!'}
    args = smart_copy(kwargs, {}, defaults=defaults)
    assert args == dict(host='localhost', port=5432, user='openerp',
                        password='keep-out!')

    # if missing a required key
    with pytest.raises(KeyError):
        args = smart_copy({}, {}, defaults=defaults)


def test_smart_copy_signature():
    with pytest.raises(TypeError):
        smart_copy({}, defaults=False)


def test_smart_copy_from_dict_to_dict():
    c = dict(c=1, d=23)
    d = dict(d=1)
    smart_copy(c, d)
    assert d == dict(c=1, d=23)


def test_smart_copy_with_plain_defaults():
    c = dict(a=1, b=2, c=3)
    d = {}
    smart_copy(c, d, defaults=('a', 'x'))
    assert d == dict(a=1, x=None)


def test_smart_copy_with_callable_default():
    def default(attr, source=None):
        return attr in ('a', 'b')

    c = dict(a=1, b='2', c='3x')
    d = {}
    smart_copy(c, d, defaults=default)
    assert d == dict(a=1, b='2')

    class inset(object):
        def __init__(self, items):
            self.items = items

        def __call__(self, attr, source=None):
            return attr in self.items

    c = dict(a=1, b='2', c='3x')
    d = {}
    smart_copy(c, d, defaults=inset('ab'))
    assert d == dict(a=1, b='2')


def test_newstyle_metaclass():
    from xoutil.objects import metaclass

    class Field(object):
        __slots__ = (str('name'), str('default'))

        def __init__(self, default):
            self.default = default

        def __get__(self, inst, owner):
            if not inst:
                return self
            return self.default

    class ModelType(type):
        pass

    class Base(object):
        def __init__(self, **attrs):
            self.__dict__.update(attrs)

    class Model(metaclass(ModelType)):
        f1 = Field(1009)
        f2 = 0

        def __init__(self, **attrs):
            self.__dict__.update(attrs)

    class Model2(Base, metaclass(ModelType)):
        pass

    class SubMeta(ModelType):
        pass

    class Submodel(Model, metaclass(SubMeta)):
        pass

    inst = Model(name='Instance')
    assert inst.f1 == 1009
    assert inst.name == 'Instance'
    assert isinstance(Model.f1, Field)
    assert type(Model) is ModelType
    assert type(Submodel) is SubMeta
    assert type(Model2) is ModelType
    assert Model2.__base__ is Base
    assert Submodel.__base__ is Model
    assert Model.__base__ is object


def test_new_style_metaclass_registration():
    import sys
    from xoutil.objects import metaclass

    class BaseMeta(type):
        classes = []

        def __new__(cls, name, bases, attrs):
            res = super(BaseMeta, cls).__new__(cls, name, bases, attrs)
            cls.classes.append(res)   # <-- side effect
            return res

    class Base(metaclass(BaseMeta)):
        pass

    class SubType(BaseMeta):
        pass

    class Egg(metaclass(SubType), Base):   # <-- metaclass first
        pass

    assert Egg.__base__ is Base   # <-- but the base is Base
    assert len(BaseMeta.classes) == 2

    class Spam(Base, metaclass(SubType)):
        'Like "Egg" but it will be registered twice in Python 2.x.'

    if sys.version_info < (3, 2):
        assert len(BaseMeta.classes) == 4  # Called twice in Python 2
    else:
        assert len(BaseMeta.classes) == 3  # Properly called once in Python 3

      # Nevertheless the bases are ok.
    assert Spam.__bases__ == (Base, )


def test_lazy():
    from xoutil.objects import lazy, setdefaultattr
    class new(object): pass
    inst = new()
    setter = lambda a: -a
    setdefaultattr(inst, 'c', lazy(setter, 10))
    assert inst.c == -10
    setdefaultattr(inst, 'c', lazy(setter, 20))
    assert inst.c == -10


# Easly creates a hierarchy of objects
class new(object):
    def __init__(self, **kwargs):
        attrs = {}
        children = {}
        for attr, value in kwargs.items():
            if '.' in attr:
                name, childattr = attr.split('.', 1)
                child = children.setdefault(name, {})
                child[childattr] = value
            else:
                attrs[attr] = value
        self.__dict__.update(attrs)
        assert set(attrs.keys()) & set(children.keys()) == set()
        for child, vals in children.items():
            setattr(self, child, new(**vals))


def test_traversing():
    from xoutil.objects import traverse, get_traverser
    obj = new(**{'a': 1, 'b.c.d': {'x': 2}, 'b.c.x': 3})
    assert traverse(obj, 'a') == 1
    assert traverse(obj, 'b.c.d.x') == 2
    assert traverse(obj, 'b.c.x') == 3
    with pytest.raises(AttributeError):
        traverse(obj, 'a.v')
    with pytest.raises(AttributeError):
        traverse(obj, 'a.b.c.d.y')

    traverser = get_traverser('a', 'b.c.d.x', 'b.c.d.y')
    with pytest.raises(AttributeError):
        traverser(obj)
    obj.b.c.d['y'] = None
    assert traverser(obj) == (1, 2, None)


def test_dict_merge_base_cases():
    from xoutil.objects import dict_merge
    base = {'a': 'a', 'd': {'attr1': 2}}
    assert dict_merge() == {}
    assert dict_merge(base) == base
    assert dict_merge(**base) == base


def test_dict_merge_simple_cases():
    from xoutil.objects import dict_merge
    first = {'a': {'attr1': 1}, 'b': {'attr1': 1}, 'c': 194, 'shared': 1}
    second = {'a': {'attr2': 2}, 'b': {'attr2': 2}, 'd': 195, 'shared': 2}
    expected = {'a': {'attr1': 1, 'attr2': 2},
                'b': {'attr1': 1, 'attr2': 2},
                'c': 194,
                'd': 195,
                'shared': 2}
    assert dict_merge(first, second) == expected
    assert dict_merge(first, **second) == expected
    assert dict_merge(second, first) == dict(expected, shared=1)
    assert dict_merge(second, **first) == dict(expected, shared=1)


def test_dict_merge_compatible_cases():
    from xoutil.objects import dict_merge
    first = {192: ['attr1', 1], 193: {'attr1', 1}}
    second = {192: ('attr2', 2), 193: ['attr2', 2]}
    assert dict_merge(first, second) == {192: ['attr1', 1, 'attr2', 2],
                                         193: {'attr1', 1, 'attr2', 2}}
    result = dict_merge(second, first)
    assert result[192] == ('attr2', 2, 'attr1', 1)
    key_193 = result[193]
    assert key_193[:2] == ['attr2', 2]
    # Since order of set's members is not defined we can't test order, we can
    # only know that they'll be in the last two positions.
    assert key_193.index('attr1') in (2, 3)
    assert key_193.index(1) in (2, 3)


def test_dict_merge_errors():
    from xoutil.objects import dict_merge
    first = {192: 192}
    second = {192: [192]}
    with pytest.raises(TypeError):
        dict_merge(second, first)
    with pytest.raises(TypeError):
        dict_merge(first, second)


def test_get_first_of():
    from xoutil.objects import get_first_of
    somedict = {"foo": "bar", "spam": "eggs"}
    assert get_first_of(somedict, "no", "foo", "spam") == 'bar'

    somedict = {"foo": "bar", "spam": "eggs"}
    assert get_first_of(somedict, "eggs") is None

    class Someobject(object): pass
    inst = Someobject()
    inst.foo = 'bar'
    inst.eggs = 'spam'
    assert get_first_of(inst, 'no', 'eggs', 'foo') == 'spam'
    assert get_first_of(inst, 'invalid') is None

    somedict = {"foo": "bar", "spam": "eggs"}
    class Someobject(object): pass
    inst = Someobject()
    inst.foo = 'bar2'
    inst.eggs = 'spam'
    assert get_first_of((somedict, inst), 'eggs') == 'spam'
    assert get_first_of((somedict, inst), 'foo') == 'bar'
    assert get_first_of((inst, somedict), 'foo') == 'bar2'
    assert get_first_of((inst, somedict), 'foobar') is None

    none = object()
    assert get_first_of((inst, somedict), 'foobar', default=none) is none
    assert get_first_of(somedict, 'foo', 'spam', pred=lambda v: len(v) > 3) == 'eggs'
    assert get_first_of(somedict, 'foo', 'spam', pred=lambda v: len(v) > 4) is None

    with pytest.raises(TypeError):
        get_first_of(None, anything=1)


def test_smart_getter():
    from xoutil.objects import smart_getter
    class new(object): pass
    o = new()
    o.attr1 = 1
    o.attr2 = 1
    getter = smart_getter(o)
    assert getter('attr1') == getter('attr2') == 1
    assert getter('attr3') is None

    getter = smart_getter(o, strict=True)
    assert getter('attr1') == getter('attr2') == 1
    with pytest.raises(AttributeError):
        assert getter('attr3') is None

    d = {'key1': 1, 'key2': 1}
    getter = smart_getter(d)
    assert getter('key1') == getter('key2') == 1
    assert getter('key3') is None

    getter = smart_getter(d, strict=True)
    assert getter('key1') == getter('key2') == 1
    with pytest.raises(KeyError):
        assert getter('key3') is None
    assert getter('key3', None) is None


def test_extract_attrs():
    from xoutil.objects import extract_attrs
    d = dict(a=(1,), b=2, c=3, x=4)
    assert extract_attrs(d, 'a') == (1,)
    assert extract_attrs(d, 'a', 'b', 'c', 'x') == ((1,), 2, 3, 4)

    with pytest.raises(AttributeError):
        assert extract_attrs(d, 'y')
    assert extract_attrs(d, 'y', default=None) is None

    class new(object):
        def __init__(self, **kw):
            self.__dict__.update(kw)

    d = new(a=(1,), b=2, c=3, x=4)
    assert extract_attrs(d, 'a') == (1,)
    assert extract_attrs(d, 'a', 'b', 'c', 'x') == ((1,), 2, 3, 4)

    with pytest.raises(AttributeError):
        assert extract_attrs(d, 'y')
    assert extract_attrs(d, 'y', default=None) is None
