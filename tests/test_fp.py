#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.tests.test_fp
# ---------------------------------------------------------------------
# Copyright (c) 2016, 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-10-08

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


def test_fp_compose():
    from xoutil.fp.tools import (
        identity,
        compose,
        pos_args,
        kw_args,
        full_args
    )

    x, obj = 15, object()
    f, g, h = x.__add__, x.__mul__, x.__xor__

    def join(*args):
        if args:
            return ' -- '.join(str(arg) for arg in args)
        # functions return 'None' when no explicit 'return' is issued.

    def plus2(value):
        return value + 2

    def plus2d(value):
        return {'stop': value + 2}

    def myrange(stop):
        return list(range(stop))

    assert compose(join, pos_args, myrange, plus2)(0) == '0 -- 1'
    assert compose(join, myrange, plus2)(0) == '[0, 1]'

    assert compose(join, myrange, kw_args, plus2d)(0) == '[0, 1]'
    assert compose(join, myrange, full_args.parse, plus2d)(0) == '[0, 1]'

    assert compose() is identity
    assert compose()(x) is x
    assert compose()(obj) is obj
    assert compose(f) is f
    assert compose(g, f)(x) == g(f(x))
    assert compose(h, g, f)(x) == h(g(f(x)))


def test_fp_tools():
    from xoutil.fp.tools import identity, compose

    x, obj = 15, object()
    f, g, h = x.__add__, x.__mul__, x.__xor__

    def join(*args):
        if args:
            return ' -- '.join(str(arg) for arg in args)
        # functions return 'None' when no explicit 'return' is issued.

    def plus2(value):
        return value + 2

    def plus2d(value):
        return {'stop': value + 2}

    def myrange(stop):
        return list(range(stop))

    assert compose(join, myrange, plus2)(0) == '[0, 1]'
    assert compose() is identity
    assert compose()(x) is x
    assert compose()(obj) is obj
    assert compose(f) is f
    assert compose(g, f)(x) == g(f(x))
    assert compose(h, g, f)(x) == h(g(f(x)))

    c = compose(*((lambda y: lambda x: x + y)(i) for i in range(6)))
    for i in range(7):
        assert c[:i](0) == sum(range(i))
