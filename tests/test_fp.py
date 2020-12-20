#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from hypothesis import strategies as s, given, example


def test_fp_compose():
    from xotl.tools.fp.tools import identity, compose, pos_args, kw_args, full_args

    x, obj = 15, object()
    f, g, h = x.__add__, x.__mul__, x.__xor__

    def join(*args):
        if args:
            return " -- ".join(str(arg) for arg in args)
        # functions return 'None' when no explicit 'return' is issued.

    def plus2(value):
        return value + 2

    def plus2d(value):
        return {"stop": value + 2}

    def myrange(stop):
        return list(range(stop))

    assert compose(join, pos_args, myrange, plus2)(0) == "0 -- 1"
    assert compose(join, myrange, plus2)(0) == "[0, 1]"

    assert compose(join, myrange, kw_args, plus2d)(0) == "[0, 1]"
    assert compose(join, myrange, full_args.parse, plus2d)(0) == "[0, 1]"

    assert compose() is identity
    assert compose()(x) is x
    assert compose()(obj) is obj
    assert compose(f) is f
    assert compose(g, f)(x) == g(f(x))
    assert compose(h, g, f)(x) == h(g(f(x)))


def test_fp_compose_wrapable():
    from functools import wraps
    from xotl.tools.fp.tools import compose

    def wrapper():
        "X"
        pass

    res = wraps(wrapper)(compose(wrapper, lambda: None))
    assert res.__name__ == wrapper.__name__
    assert res.__doc__ == wrapper.__doc__
    assert res.__module__ == wrapper.__module__


def test_fp_tools():
    from xotl.tools.fp.tools import identity, compose

    x, obj = 15, object()
    f, g, h = x.__add__, x.__mul__, x.__xor__

    def join(*args):
        if args:
            return " -- ".join(str(arg) for arg in args)
        # functions return 'None' when no explicit 'return' is issued.

    def plus2(value):
        return value + 2

    def plus2d(value):
        return {"stop": value + 2}

    def myrange(stop):
        return list(range(stop))

    assert compose(join, myrange, plus2)(0) == "[0, 1]"
    assert compose() is identity
    assert compose()(x) is x
    assert compose()(obj) is obj
    assert compose(f) is f
    assert compose(g, f)(x) == g(f(x))
    assert compose(h, g, f)(x) == h(g(f(x)))

    c = compose(*((lambda y: lambda x: x + y)(i) for i in range(6)))
    for i in range(7):
        assert c[:i](0) == sum(range(i))


@given(s.integers(min_value=0, max_value=20))
@example(4)
def test_fp_kleisli_compose(n):
    from xotl.tools.fp.iterators import kleisli_compose

    def fullrange(n):
        "[0..n]"
        return range(n + 1)

    def odds(n):
        return [x for x in fullrange(n) if x % 2 != 0]

    odd_seqs = kleisli_compose(odds, fullrange)
    assert list(odd_seqs(n)) == [z for y in fullrange(n) for z in odds(y)]
    id_ = lambda x: [x]
    pad = (id_,) * n
    args = pad + (odds,) + pad + (fullrange,) + pad
    odd_seqs = kleisli_compose(*args)
    assert list(odd_seqs(n)) == [z for y in fullrange(n) for z in odds(y)]

    odd_seqs = kleisli_compose(fullrange, odds)
    assert list(odd_seqs(n)) == [z for y in odds(n) for z in fullrange(y)]
    args = pad + (fullrange,) + pad + (odds,) + pad
    odd_seqs = kleisli_compose(*args)
    assert list(odd_seqs(n)) == [z for y in odds(n) for z in fullrange(y)]


def test_fp_kleisli_compose4():
    from xotl.tools.fp.iterators import kleisli_compose

    def fullrange(n):
        "[0..n]"
        return range(n + 1)

    def odds(n):
        return [x for x in fullrange(n) if x % 2 != 0]

    id_ = lambda x: [x]
    odd_seqs = kleisli_compose(odds, fullrange)
    assert list(odd_seqs(4)) == [1, 1, 1, 3, 1, 3]
    odd_seqs = kleisli_compose(id_, odds, id_, id_, fullrange, id_)
    assert list(odd_seqs(4)) == [1, 1, 1, 3, 1, 3]

    odd_seqs = kleisli_compose(fullrange, odds)
    assert list(odd_seqs(4)) == [0, 1, 0, 1, 2, 3]
    odd_seqs = kleisli_compose(id_, fullrange, id_, id_, odds, id_)
    assert list(odd_seqs(4)) == [0, 1, 0, 1, 2, 3]


anything = (
    s.integers()
    | s.dictionaries(s.text(), s.integers())
    | s.text()
    | s.tuples(s.integers())
)
anyargs = s.tuples(anything)


@given(anything, anyargs)
def test_constant(val, args):
    from xotl.tools.fp.tools import constant

    fn = constant(val)
    assert fn(*args) is val


if __name__ == "__main__":
    # Allow to run this test as an independent python script, for example:
    #   monkeytype run tests/test_fp.py
    test_fp_compose()
    test_fp_compose_wrapable()
    test_fp_tools()
    test_fp_kleisli_compose()
    test_fp_kleisli_compose4()
    test_constant()
