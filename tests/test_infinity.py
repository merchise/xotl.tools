#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import pickle
from functools import total_ordering

from hypothesis import given, strategies as s
from xotl.tools.infinity import Infinity, InfinityType


@given(s.floats() | s.integers())
def test_comparable_with_numbers(x):
    assert -Infinity < x < Infinity


@given(s.dates() | s.datetimes())
def test_comparable_with_dates(x):
    assert -Infinity < x < Infinity


def test_infinity_hashable():
    hash(Infinity)
    hash(-Infinity)


def test_singleton():
    assert Infinity is InfinityType(+1)
    assert -Infinity is InfinityType(-1)


@given(
    s.sampled_from([Infinity, -Infinity]),
    s.sampled_from([pickle.HIGHEST_PROTOCOL, pickle.DEFAULT_PROTOCOL]),
)
def test_pickable(inf, proto):
    serialized = pickle.dumps(inf, proto)
    assert inf is pickle.loads(serialized)


@total_ordering
class WrappedValue:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, WrappedValue):
            return self.value == other.value
        else:
            return self.value == other

    def __le__(self, other):
        if isinstance(other, WrappedValue):
            return self.value <= other.value
        else:
            return self.value <= other


@given((s.floats() | s.integers()).map(lambda x: WrappedValue(x)))
def test_comparable_with_wrapped_numbers(x):
    assert -Infinity < x < Infinity


@given((s.dates() | s.datetimes()).map(lambda x: WrappedValue(x)))
def test_comparable_with_wrapped_dates(x):
    assert -Infinity < x < Infinity
