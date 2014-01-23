#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_datetime
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-03-25

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

import pytest

from xoutil.datetime import date
from xoutil.datetime import daterange


def test_daterange_stop_only():
    result = list(daterange(date(1978, 10, 21)))
    assert result[0] == date(1978, 10, 1)
    assert result[-1] == date(1978, 10, 20)


def test_daterange_empty():
    assert [] == list(daterange(date(1978, 10, 21), -2))
    assert [] == list(daterange(date(1978, 10, 21), date(1978, 10, 10)))
    assert [] == list(daterange(date(1978, 10, 10), date(1978, 10, 20), -1))


def test_daterange_going_back_in_time():
    result = list(daterange(date(1978, 10, 21), -2, -1))
    assert result[0] == date(1978, 10, 21)
    assert result[-1] == date(1978, 10, 20)


def test_daterange_invalid_int_stop():
    with pytest.raises(TypeError):
        daterange(10)


def test_daterange_invalid_step():
    with pytest.raises(ValueError):
        daterange(None, date(1978, 10, 21), 0)
