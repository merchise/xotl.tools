#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import sys
import pytest

from hypothesis import given, strategies as s

from xoutil.infinity import Infinity


@given(s.floats() | s.integers())
def test_comparable_with_numbers(x):
    assert -Infinity < x < Infinity


@given(s.dates() | s.datetimes())
def test_comparable_with_dates(x):
    assert -Infinity < x < Infinity
