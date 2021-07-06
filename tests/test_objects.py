#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import pytest

from xotl.tools.objects import (
    fulldir,
    smart_copy,
    lazy,
    setdefaultattr,
    traverse,
    get_traverser,
    dict_merge,
    get_first_of,
    smart_getter,
    smart_setter,
    extract_attrs,
    copy_class,
    validate_attrs,
    memoized_property,
    classproperty,
    xproperty,
    staticproperty,
    multi_getter,
    save_attributes,
)
from xotl.tools.symbols import Unset
from xotl.tools.future.types import SimpleNamespace as new


def test_smart_copy():
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
    assert target["_d"] == 5


def test_smart_copy_with_defaults():
    defaults = {
        "host": "localhost",
        "port": 5432,
        "user": "openerp",
        "password": (KeyError, "{key}"),
    }
    kwargs = {"password": "keep-out!"}
    args = smart_copy(kwargs, {}, defaults=defaults)
    assert args == dict(
        host="localhost", port=5432, user="openerp", password="keep-out!"
    )

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
    smart_copy(c, d, defaults=("a", "x"))
    assert d == dict(a=1, x=None)


def test_smart_copy_with_callable_default():
    def default(attr, source=None):
        return attr in ("a", "b")

    c = dict(a=1, b="2", c="3x")
    d = {}
    smart_copy(c, d, defaults=default)
    assert d == dict(a=1, b="2")

    class inset:
        def __init__(self, items):
            self.items = items

        def __call__(self, attr, source=None):
            return attr in self.items

    c = dict(a=1, b="2", c="3x")
    d = {}
    smart_copy(c, d, defaults=inset("ab"))
    assert d == dict(a=1, b="2")


def test_fulldir():
    assert {"__getitem__", "get", "items", "keys"} < fulldir({})


def test_newstyle_metaclass():
    class Field:
        __slots__ = (str("name"), str("default"))

        def __init__(self, default):
            self.default = default

        def __get__(self, inst, owner):
            if not inst:
                return self
            return self.default

    class ModelType(type):
        pass

    class Base:
        def __init__(self, **attrs):
            self.__dict__.update(attrs)

    class Model(metaclass=ModelType):
        f1 = Field(1009)
        f2 = 0

        def __init__(self, **attrs):
            self.__dict__.update(attrs)

    class Model2(Base, metaclass=ModelType):
        pass

    class SubMeta(ModelType):
        pass

    class Submodel(Model, metaclass=SubMeta):
        pass

    inst = Model(name="Instance")
    assert inst.f1 == 1009
    assert inst.name == "Instance"
    assert isinstance(Model.f1, Field)
    assert type(Model) is ModelType
    assert type(Submodel) is SubMeta
    assert type(Model2) is ModelType
    assert Model2.__base__ is Base
    assert Submodel.__base__ is Model
    assert Model.__base__ is object


def test_new_style_metaclass_registration():
    class BaseMeta(type):
        classes = []

        def __new__(cls, name, bases, attrs):
            res = super(BaseMeta, cls).__new__(cls, name, bases, attrs)
            cls.classes.append(res)  # <-- side effect
            return res

    class Base(metaclass=BaseMeta):
        pass

    class SubType(BaseMeta):
        pass

    class Egg(Base, metaclass=SubType):
        pass

    assert Egg.__base__ is Base
    assert len(BaseMeta.classes) == 2

    class Spam(Base, metaclass=SubType):
        'Like "Egg" but it will be registered twice in Python 2.x.'

    assert len(BaseMeta.classes) == 3  # Properly called once in Python 3

    # Nevertheless the bases are ok.
    assert Spam.__bases__ == (Base,)


def test_lazy():
    class new:
        pass

    inst = new()
    setter = lambda a: -a
    setdefaultattr(inst, "c", lazy(setter, 10))
    assert inst.c == -10
    setdefaultattr(inst, "c", lazy(setter, 20))
    assert inst.c == -10


# Easly creates a hierarchy of objects
class New:
    def __init__(self, **kwargs):
        attrs = {}
        children = {}
        for attr, value in kwargs.items():
            if "." in attr:
                name, childattr = attr.split(".", 1)
                child = children.setdefault(name, {})
                child[childattr] = value
            else:
                attrs[attr] = value
        self.__dict__.update(attrs)
        assert set(attrs.keys()) & set(children.keys()) == set()
        for child, vals in children.items():
            setattr(self, child, New(**vals))


def test_traversing():
    obj = new(**{"a": 1, "b": new(c=new(d={"x": 2}, x=3))})
    assert traverse(obj, "a") == 1
    assert traverse(obj, "b.c.d.x") == 2
    assert traverse(obj, "b.c.x") == 3
    with pytest.raises(AttributeError):
        traverse(obj, "a.v")
    with pytest.raises(AttributeError):
        traverse(obj, "a.b.c.d.y")

    traverser = get_traverser("a", "b.c.d.x", "b.c.d.y")
    with pytest.raises(AttributeError):
        traverser(obj)
    obj.b.c.d["y"] = None
    assert traverser(obj) == (1, 2, None)


def test_traversing_bug_ignoring_getter():
    from unittest import mock
    from xoutil.objects import traverse

    sentinel = object()

    class Me:
        def __getattr__(self, attr):
            return self

    return_sentinel = mock.Mock(return_value=sentinel)

    me = Me()
    assert traverse(me, "x.y", getter=return_sentinel) is sentinel
    assert return_sentinel.called


def test_dict_merge_base_cases():
    base = {"a": "a", "d": {"attr1": 2}}
    assert dict_merge() == {}
    assert dict_merge(base) == base
    assert dict_merge(**base) == base


def test_dict_merge_simple_cases():
    first = {"a": {"attr1": 1}, "b": {"attr1": 1}, "c": 194, "shared": 1}
    second = {"a": {"attr2": 2}, "b": {"attr2": 2}, "d": 195, "shared": 2}
    expected = {
        "a": {"attr1": 1, "attr2": 2},
        "b": {"attr1": 1, "attr2": 2},
        "c": 194,
        "d": 195,
        "shared": 2,
    }
    assert dict_merge(first, second) == expected
    assert dict_merge(first, **second) == expected
    assert dict_merge(second, first) == dict(expected, shared=1)
    assert dict_merge(second, **first) == dict(expected, shared=1)


def test_dict_merge_compatible_cases():
    first = {192: ["attr1", 1], 193: {"attr1", 1}}
    second = {192: ("attr2", 2), 193: ["attr2", 2]}
    assert dict_merge(first, second) == {
        192: ["attr1", 1, "attr2", 2],
        193: {"attr1", 1, "attr2", 2},
    }
    result = dict_merge(second, first)
    assert result[192] == ("attr2", 2, "attr1", 1)
    key_193 = result[193]
    assert key_193[:2] == ["attr2", 2]
    # Since order of set's members is not defined we can't test order, we can
    # only know that they'll be in the last two positions.
    assert key_193.index("attr1") in (2, 3)
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
    somedict = {"foo": "bar", "spam": "eggs"}
    assert get_first_of(somedict, "no", "foo", "spam") == "bar"

    somedict = {"foo": "bar", "spam": "eggs"}
    assert get_first_of(somedict, "eggs") is None

    class Someobject:
        pass

    inst = Someobject()
    inst.foo = "bar"
    inst.eggs = "spam"
    assert get_first_of(inst, "no", "eggs", "foo") == "spam"
    assert get_first_of(inst, "invalid") is None

    somedict = {"foo": "bar", "spam": "eggs"}

    class Someobject:
        pass

    inst = Someobject()
    inst.foo = "bar2"
    inst.eggs = "spam"
    assert get_first_of((somedict, inst), "eggs") == "spam"
    assert get_first_of((somedict, inst), "foo") == "bar"
    assert get_first_of((inst, somedict), "foo") == "bar2"
    assert get_first_of((inst, somedict), "foobar") is None

    none = object()
    assert get_first_of((inst, somedict), "foobar", default=none) is none
    _eggs = get_first_of(somedict, "foo", "spam", pred=lambda v: len(v) > 3)
    assert _eggs == "eggs"
    _none = get_first_of(somedict, "foo", "spam", pred=lambda v: len(v) > 4)
    assert _none is None

    with pytest.raises(TypeError):
        get_first_of(None, anything=1)


def test_smart_getter():
    o = new()
    o.attr1 = 1
    o.attr2 = 1
    getter = smart_getter(o)
    assert getter("attr1") == getter("attr2") == 1
    assert getter("attr3") is None

    getter = smart_getter(o, strict=True)
    assert getter("attr1") == getter("attr2") == 1
    with pytest.raises(AttributeError):
        assert getter("attr3") is None

    d = {"key1": 1, "key2": 1}
    getter = smart_getter(d)
    assert getter("key1") == getter("key2") == 1
    assert getter("key3") is None

    getter = smart_getter(d, strict=True)
    assert getter("key1") == getter("key2") == 1
    with pytest.raises(KeyError):
        assert getter("key3") is None
    assert getter("key3", None) is None


def test_smart_setter():
    class new:
        pass

    o = new()
    setter = smart_setter(o)
    setter("attr1", 1)
    setter("attr2", 1)
    assert o.attr1 == o.attr2 == 1

    d = {"key1": 1, "key2": 1}
    setter = smart_setter(d)
    setter("key1", 10)
    assert d["key1"] == 10


def test_extract_attrs():
    d = dict(a=(1,), b=2, c=3, x=4)
    assert extract_attrs(d, "a") == (1,)
    assert extract_attrs(d, "a", "b", "c", "x") == ((1,), 2, 3, 4)

    with pytest.raises(AttributeError):
        assert extract_attrs(d, "y")
    assert extract_attrs(d, "y", default=None) is None

    class new:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    d = new(a=(1,), b=2, c=3, x=4)
    assert extract_attrs(d, "a") == (1,)
    assert extract_attrs(d, "a", "b", "c", "x") == ((1,), 2, 3, 4)

    with pytest.raises(AttributeError):
        assert extract_attrs(d, "y")
    assert extract_attrs(d, "y", default=None) is None


def test_copy_class():
    u = str

    class MetaFoo(type):
        pass

    class Foo(metaclass=MetaFoo):
        a = 1
        b = 2
        c = 3
        d = 4

    class Baz(Foo):
        e = 5

    index = {k: getattr(Foo, k) for k in "abcd"}
    Bar = copy_class(Foo)
    assert Bar.a == Foo.a and Bar.b and Bar.c and Bar.d

    Egg = copy_class(Foo, ignores=["b", "c"])
    assert getattr(Egg, "b", Unset) is Unset

    Egg = copy_class(
        Foo,
        ignores=[lambda k: index.get(k) and index.get(k) > 2],
    )
    assert Egg.a == Foo.a
    assert getattr(Egg, "c", Unset) is Unset

    Named = copy_class(Foo, new_name="Named")
    assert Named.__name__ == "Named"

    Named = copy_class(Foo, new_name=u("Named"))
    assert Named.__name__ == "Named"

    import fnmatch

    pattern = lambda attr: fnmatch.fnmatch(attr, "a*")
    Egg = copy_class(Foo, ignores=[pattern])
    assert getattr(Egg, "a", Unset) is Unset

    import re

    _pattern = re.compile("^a")
    pattern = lambda attr: _pattern.match(attr)
    Egg = copy_class(Foo, ignores=[pattern])
    assert getattr(Egg, "a", Unset) is Unset


def test_validate_attrs():
    class Person:
        def __init__(self, **kwargs):
            for which in kwargs:
                setattr(self, which, kwargs[which])

    source = Person(name="Manuel", age=33, sex="male")
    target = {"name": "Manuel", "age": 4, "sex": "male"}

    assert validate_attrs(
        source, target, force_equals=("sex",), force_differents=("age",)
    )

    assert not validate_attrs(source, target, force_equals=("age",))


@pytest.mark.xfail()
def test_memoized_classproperty():
    current = 1

    class Foobar:
        @memoized_property
        @classproperty
        def prop(cls):
            return current

        @classproperty
        @memoized_property
        def prop2(cls):
            return current

    assert Foobar.prop == current
    current += 1
    assert Foobar.prop != current


def test_properties():
    _x = "static"

    class Foobar:
        _x = "class"

        def __init__(self):
            self._x = "instance"

        @xproperty
        def x(self):
            return self._x

        @classproperty
        def cprop(cls):
            return cls._x

        @staticproperty
        def sprop():
            return _x

    f = Foobar()

    assert Foobar.x == "class"
    assert f.x == "instance"

    assert Foobar.cprop == "class"
    assert f.cprop == "class"

    assert Foobar.sprop == "static"
    assert f.sprop == "static"


def test_multi_getter_failure():
    """`multi_getter` is not the same as `traverse`.

    When a collection of identifiers is given, it get the first valid value
    (see the documentation).

    """
    from xoutil.objects import traverse

    class new:
        def __init__(self, **k):
            self.__dict__.update(k)

    top = new(d=dict(a=1, b=2), a=10, b=20)

    assert traverse(top, "d.a") == 1
    assert next(multi_getter(top, ("d", "a"))) == {"a": 1, "b": 2}


def test_save_attributes():
    from xoutil.future.types import SimpleNamespace as new
    from xoutil.objects import save_attributes

    obj = new(a=1, b=2)
    with save_attributes(obj, "a"):
        obj.a = 2
        obj.b = 3
        assert obj.a == 2

    assert obj.a == 1
    assert obj.b == 3


def test_temp_attributes():
    from xotl.tools.future.types import SimpleNamespace as new
    from xotl.tools.objects import temp_attributes

    obj = new(a=1, b=2)
    with temp_attributes(obj, dict(a=2)):
        assert obj.a == 2
        assert obj.b == 2
        obj.b = 3

    assert obj.a == 1
    assert obj.b == 3


def test_save_raises_errors():
    from xotl.tools.future.types import SimpleNamespace as new

    getter = lambda o: lambda a: getattr(o, a)
    obj = new(a=1, b=2)
    with pytest.raises(AttributeError):
        with save_attributes(obj, "c", getter=getter):
            pass

    with save_attributes(obj, "x"):
        pass

    assert obj.x is None

    obj = object()
    with pytest.raises(AttributeError):
        with save_attributes(obj, "x"):
            pass


def test_import_object():
    from xotl.tools.objects import import_object

    assert import_object("xotl.tools.objects.import_object") is import_object
    assert import_object("xotl.tools.objects:import_object") is import_object


def test_delegator():
    from xotl.tools.objects import delegator

    class Bar:
        x = object()

    class Foo(delegator("egg", {"x1": "x", "x2": "spam"})):
        def __init__(self):
            self.egg = Bar()

    foo = Foo()
    assert foo.x1 is foo.egg.x

    with pytest.raises(AttributeError):
        foo.x2


def test_final_subclasses():
    from xotl.tools.objects import get_branch_subclasses

    class Base:
        pass

    class Subclass(Base):
        pass

    class Final(Subclass):
        pass

    class SubSub(Subclass):
        pass

    class Final2(SubSub):
        pass

    assert set(get_branch_subclasses(Base)) == {Final, Final2}
    assert set(get_branch_subclasses(Final, include_this=False)) == set([])


def test_FinalSubclassEnumeration():
    from xotl.tools.objects import FinalSubclassEnumeration

    class Base:
        pass

    enum = FinalSubclassEnumeration(Base)
    enum2 = FinalSubclassEnumeration(Base, dynamic=False)

    assert not enum.__members__
    assert not enum2.__members__

    class Subclass(Base):
        pass

    class Final(Subclass):
        pass

    assert enum.Final is Final
    assert not enum2.__members__

    enum2.invalidate_cache()
    assert enum2.Final is Final
