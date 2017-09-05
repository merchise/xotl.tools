#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# test_infinity
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-08-29


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import sys
import pytest

from hypothesis import given, strategies as s

from xoutil.infinity import Infinity


@given(s.floats() | s.integers())
def test_comparable_with_numbers(x):
    assert -Infinity < x < Infinity


@given(s.dates() | s.datetimes())
def test_comparable_with_dates(x):
    if sys.version_info < (3, 0):
        # In Python 2.7, x < Infinity fails because `date` implements that
        # __lt__ itself and Python 2 does not reverse the operation when it
        # fails.
        assert -Infinity < x
        assert Infinity > x

        with pytest.raises(TypeError):
            x < Infinity
    else:
        assert -Infinity < x < Infinity
