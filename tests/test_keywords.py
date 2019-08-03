#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xotl.tools.keywords import getkwd, setkwd, kwd_getter, kwd_setter, org_kwd


def test_keywords():
    class Foobar:
        pass

    proper = lambda v: isinstance(v, type) and issubclass(v, Foobar)
    obj = Foobar()
    names = {"if", "and", "or", "abc", "xyz"}
    for name in names:
        setkwd(obj, name, type(name.title(), (Foobar,), {}))
    for name, value in vars(obj).items():
        if proper(value):
            assert org_kwd(name).title() == value.__name__
    kwd_setter(obj)("else", 123)
    assert obj.if_ is kwd_getter(obj)("if")
    assert obj.and_ is getkwd(obj, "and")
    assert obj.xyz is getkwd(obj, "xyz")
    assert obj.else_ is getkwd(obj, "else")
    keys = {org_kwd(n) for n, v in vars(obj).items() if proper(v)}
    assert keys == names
