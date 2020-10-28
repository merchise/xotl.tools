#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#


def test_nameof():
    from xotl.tools.tools import nameof

    class foobar:
        pass

    singletons = (None, True, False, Ellipsis, NotImplemented)

    assert nameof(foobar) == nameof(foobar()) == "foobar"
    assert nameof(object) == "object"
    assert nameof(test_nameof) == "test_nameof"

    assert nameof(lambda x: x) == "<lambda>"

    assert [nameof(s) for s in singletons] == [
        "None",
        "True",
        "False",
        "Ellipsis",
        "NotImplemented",
    ]

    assert nameof(1) == "int"
    assert nameof(1.0) == "float"


# TODO: Add tests for remainder functions in this module.
