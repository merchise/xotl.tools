#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import unittest


def test_iscollection():
    # TODO: move this test to equivalent for `xotl.tools.values.simple.logic_collection_coerce`
    from collections import UserDict, UserList

    def is_collection(arg):
        from collections.abc import Iterable, Mapping

        avoid = (Mapping, str)
        return isinstance(arg, Iterable) and not isinstance(arg, avoid)

    assert is_collection("all strings are iterable") is False
    assert is_collection(1) is False
    assert is_collection(range(1)) is True
    assert is_collection({}) is False
    assert is_collection(tuple()) is True
    assert is_collection(set()) is True
    assert is_collection(a for a in range(100)) is True

    class Foobar(UserList):
        pass

    assert is_collection(Foobar()) is True

    class Foobar(UserDict):
        pass

    assert is_collection(Foobar()) is False


class NoneTypeTests(unittest.TestCase):
    "To avoid FlyCheck errors"

    def test_identity(self):
        from xotl.tools.future.types import NoneType

        self.assertIs(NoneType, type(None))
