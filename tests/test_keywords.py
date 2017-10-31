#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# tests.test_keywords
#----------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-11-19


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from xoutil.keywords import getkwd, setkwd, kwd_getter, kwd_setter, org_kwd


def test_keywords():
    from xoutil.eight import iteritems

    class Foobar(object):
        pass

    proper = lambda v: isinstance(v, type) and issubclass(v, Foobar)
    obj = Foobar()
    names = {'if', 'and', 'or', 'abc', 'xyz'}
    for name in names:
        setkwd(obj, name, type(name.title(), (Foobar,), {}))
    for name, value in iteritems(vars(obj)):
        if proper(value):
            assert org_kwd(name).title() == value.__name__
    kwd_setter(obj)('else', 123)
    assert obj.if_ is kwd_getter(obj)('if')
    assert obj.and_ is getkwd(obj, 'and')
    assert obj.xyz is getkwd(obj, 'xyz')
    assert obj.else_ is getkwd(obj, 'else')
    keys = {org_kwd(n) for n, v in iteritems(vars(obj)) if proper(v)}
    assert keys == names
