#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import pytest
from xotl.tools.versions import python_version
from xotl.tools.future.collections import OrderedSmartDict

PYPY = python_version.pypy


def test_nameof():
    from xotl.tools.names import nameof, simple_name
    from collections import OrderedDict as sorted_dict

    assert nameof(sorted_dict) == "sorted_dict"
    assert nameof(sorted_dict, inner=True) == "OrderedDict"
    sd = sorted_dict(x=1, y=2)
    assert nameof(sd) == "sd"
    assert nameof(sd, typed=True) == "sorted_dict"
    assert nameof(sd, inner=True, typed=True) == "OrderedDict"
    s = "foobar"
    assert nameof(s, inner=True) == "foobar"
    # The following needs to be tested outside the assert, cause in Py3.3,
    # py.test rewrites the assert sentences and the local scope `nameof`
    # searched is not reached properly.
    passed = nameof("foobar") == "s"
    assert passed

    i = 1
    assert nameof(i) == "i"
    assert nameof(i, inner=True) == "1"
    assert nameof(i, typed=True) == "int"
    assert hex(id(sd)) in nameof(sd, inner=True)
    values = (None, True, False, BaseException, int, dict, object)
    names = [simple_name(v) for v in values]
    names.sort()
    assert names == ["BaseException", "False", "None", "True", "dict", "int", "object"]


def test_nameof_methods():
    from xotl.tools.names import nameof, simple_name

    class Foobar:
        def __init__(self):
            self.attr = "foobar"

        def first(self):
            pass

        @staticmethod
        def second():
            pass

        @classmethod
        def third(cls):
            pass

    obj = Foobar()
    attrs = (getattr(obj, n) for n in dir(obj) if not n.startswith("_"))
    attrs = (v for v in attrs if callable(v))
    names = nameof(*attrs)
    names.sort()
    assert names == ["first", "second", "third"]
    attrs = (getattr(obj, n) for n in dir(obj) if not n.startswith("_"))
    attrs = (v for v in attrs if callable(v))
    names = [simple_name(v, join=False) for v in attrs]
    names.sort()
    assert names == ["first", "second", "third"]


@pytest.mark.skipif(PYPY, reason="'OrderedDict' is in '_pypy_collections'")
def test_fullnameof():
    from xotl.tools.names import nameof, simple_name

    _name = "collections.OrderedDict"
    from collections import OrderedDict as sorted_dict

    assert nameof(sorted_dict, full=True) == "test_fullnameof.sorted_dict"
    assert nameof(sorted_dict, inner=True, full=True) == _name
    sd = sorted_dict(x=1, y=2)
    assert nameof(sd, full=True) == "test_fullnameof.sd"
    assert nameof(sd, typed=True, full=True) == "test_fullnameof.sorted_dict"
    assert nameof(sd, inner=True, typed=True, full=True) == _name
    assert simple_name(simple_name) == "xotl.tools.names.simple_name"
    assert simple_name(sd) == "collections.OrderedDict"


@pytest.mark.skipif(PYPY, reason="'OrderedDict' is in '_pypy_collections'")
def test_fullnameof_no_rename():
    from xotl.tools.names import nameof
    from collections import OrderedDict

    _full_name = "test_fullnameof_no_rename.OrderedDict"
    _name = "collections.OrderedDict"
    assert nameof(OrderedDict, full=True) == _full_name
    assert nameof(OrderedDict, inner=True, full=True) == _name


def test_module_level_name():
    from xotl.tools.names import nameof

    assert nameof(OrderedSmartDict) == "OrderedSmartDict"
    assert nameof(OrderedSmartDict, typed=True) == "OrderedSmartDict"


def test_module_level_name_isolated():
    from xotl.tools.names import nameof, simple_name

    full_name_1 = "tests.test_names.OrderedSmartDict"
    full_name_2 = "xotl.tools.future.collections.OrderedSmartDict"
    assert nameof(OrderedSmartDict, full=True) == full_name_1
    assert simple_name(OrderedSmartDict) == full_name_2
