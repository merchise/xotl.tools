#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import sys
from xotl.tools.values import file_coerce, positive_int_coerce as positive_int

# old params
from xotl.tools.params import ParamSchemeRow as row, ParamScheme as scheme


sample_scheme = scheme(
    row("stream", 0, -1, "output", default=sys.stdout, coerce=file_coerce),
    row("indent", 0, 1, default=1, coerce=positive_int),
    row("width", 0, 1, 2, "max_width", default=79, coerce=positive_int),
    row("newline", default="\n", coerce=(str,)),
)

del file_coerce, positive_int


def test_basic_params():
    def get_values(*args, **kwargs):
        return sample_scheme(args, kwargs, strict=False)

    def foobar(**kwargs):
        res = sample_scheme.defaults
        res.update(kwargs)
        return res

    one, two = get_values(4, 80), foobar(indent=4, width=80)
    assert one == two, "\n{} != \n{}".format(one, two)
    one, two = get_values(2), foobar(indent=2)
    assert one == two, "\n{} != \n{}".format(one, two)
    one = get_values(80, indent=4, extra="I'm OK!")
    two = foobar(width=80, indent=4, extra="I'm OK!")
    assert one == two, "\n{} != \n{}".format(one, two)
    one, two = get_values(width=80), foobar(width=80)
    assert one == two, "\n{} != \n{}".format(one, two)
    one = get_values(sys.stderr, 4, 80)
    two = foobar(indent=4, width=80, stream=sys.stderr)
    assert one == two, "\n{} != \n{}".format(one, two)
    one = get_values(4, sys.stderr, newline="\n\r")
    two = foobar(indent=4, stream=sys.stderr, newline="\n\r")
    assert one == two, "\n{} != \n{}".format(one, two)
    one = get_values(4, output=sys.stderr)
    two = foobar(indent=4, stream=sys.stderr)
    assert one == two, "\n{} != \n{}".format(one, two)
    one, two = get_values(4, max_width=80), foobar(indent=4, width=80)
    assert one == two, "\n{} != \n{}".format(one, two)


def test_param_errors():
    def get_values(*args, **kwargs):
        return sample_scheme(args, kwargs)

    def error_repr(error):
        return "{}()".format(type(error).__name__, error)

    msg = 'Must raised "{}", \n\tnot {}'

    try:
        get_values(sys.stderr, 4, output=sys.stderr)
        assert False, "Should raise TypeError"
    except TypeError:
        pass
    except BaseException as error:
        assert False, msg.format(TypeError.__name__, error_repr(error))
    try:
        get_values(4, -79)
        assert False, "Should raise TypeError"
    except TypeError:
        pass
    except BaseException as error:
        assert False, msg.format(TypeError.__name__, error_repr(error))
    try:
        get_values(80, indent=4, extra="I'm not OK!")
        assert False, "Should raise TypeError"
    except TypeError:
        pass
    except BaseException as error:
        assert False, msg.format(TypeError.__name__, error_repr(error))


def test_pop_keyword_values():
    from xotl.tools.symbols import Unset
    from xotl.tools.params import pop_keyword_values as popkw, Undefined

    kwds = dict(default=None, values=[1, 2, 3], collector=sum)
    names = (("func", "collector"), "default")

    assert popkw(dict(kwds), "values", *names) == [[1, 2, 3], sum, None]

    try:
        assert popkw(dict(kwds), *names) == "whatever"
    except TypeError:
        assert True

    try:
        assert popkw(dict(kwds), *names, ignore_error=True) == [sum, None]
    except TypeError:
        assert False

    test = [Undefined, [1, 2, 3], sum, None]
    assert popkw(dict(kwds), "x", "values", *names) == test

    test = [None, [1, 2, 3], sum, None]
    assert popkw(dict(kwds), "x", "values", *names, default=None) == test

    test = [Unset, [1, 2, 3], sum, None]
    defaults = dict(x=Unset)
    assert popkw(dict(kwds), "x", "values", *names, defaults=defaults) == test
