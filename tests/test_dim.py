#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# test_units
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-05-12

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import pytest
from hypothesis import given, strategies as s

from xoutil.dim.meta import (
    Signature,
    Quantity,
    QuantityType,
    Scalar,
    UNIT,
)


def test_usage():
    @QuantityType.new
    class L(object):
        metre = UNIT
        kilometre = 1000 * metre

    @QuantityType.new
    class T(object):
        second = UNIT

    m, km = L.metre, L.kilometre
    s = T.second

    assert isinstance(m, L)
    assert not isinstance(1, L)
    assert isinstance(s, T)

    assert -km == -1 * km == -(1000 * m)
    assert +km == km

    Speed = L/T

    assert isinstance(m / s, Speed)
    assert not isinstance(m, T)

    assert hasattr(L / T, 'metre_per_second')

    assert 10 * km == 10000 * m
    assert m < km

    with pytest.raises(TypeError):
        10 + 10 * km

    with pytest.raises(TypeError):
        m + s

    assert Speed.metre_per_second == m / s

    Acceleration = L / (T * T)
    assert hasattr(Acceleration, 'metre_per_second_squared')
    # however:
    Not_Acceleration = L / T * T
    assert hasattr(Not_Acceleration, 'metre_per_second_second')
    assert L == Not_Acceleration, 'It is the same as Length'


def test_effort():
    @QuantityType.new
    class Workforce(object):
        men = UNIT

    @QuantityType.new
    class Time(object):
        second = UNIT

    class Effort(Workforce * Time):
        # Since the canonical unit of a composed quantity type is built from
        # the canonical units of the operands, but the true "canonical type"
        # of effort is usually men-hour we re-introduce it.
        men_hour = 60

    assert Effort.men_hour > Effort.men_second


def test_scalar_downgrade():
    from xoutil.dim.app.standard import L
    km = L.km
    assert not isinstance(km / km, Quantity)
    assert km / km == 1
    assert not isinstance(km // km, Quantity)
    assert km // km == 1

    assert not isinstance(1 / km * km, Quantity)
    assert float(1 / km * km)


def test_natural_downgrade():
    from xoutil.dim.app.standard import L
    km, cm = L.km, L.cm
    assert float(km) == 1000
    assert int(cm) == 0


def test_decimals():
    import decimal
    from xoutil.dim.app.standard import m
    with pytest.raises(TypeError):
        third = decimal.Decimal('0.33') * m
        assert third < m


def test_signatures():
    distance = Signature('m')
    time = Signature('s')
    freq = 1 / time
    speed = distance / time
    acceleration = speed / time
    assert acceleration == distance / (time * Signature('s'))
    assert speed == distance * freq
    assert speed**3 == speed * speed * speed
    assert speed**0 == Signature() == speed / speed
    assert speed**-3 == 1 / (speed**3)


def test_quantity_math():
    metre = m = Quantity(1, Signature('m'))
    second = Quantity(1, Signature('s'))

    with pytest.raises(TypeError):
        metre < second

    assert metre < 2 * metre < (metre + 2 * metre)
    assert metre * metre == Quantity(1, Signature('mm'))
    assert metre / second == Quantity(1, Signature('m', 's'))
    assert metre * metre * metre == metre**3
    assert 1/(metre * metre * metre) == metre**-3

    assert 1000 * m % 3 == 1 * m
    assert 5 % (2 * m) == 1 / m
    assert 5 / (2 * m) == 2.5 / m

    with pytest.raises(TypeError):
        5 ** (2*m)


def test_quantity_type_definitions():
    from xoutil.dim.app.standard import Length as Distance, Time
    assert isinstance(Distance, QuantityType)
    assert isinstance(Time, QuantityType)
    assert isinstance(Distance / Time, QuantityType)
    assert isinstance(Distance**2, QuantityType)
    assert Distance * Distance == Distance**2

    assert Time / Time == Scalar
    assert Time / Time * Time == Time

    with pytest.raises(TypeError):
        Distance + Time

    with pytest.raises(TypeError):
        Distance - Time

    assert Distance**1 is Distance

    with pytest.raises(TypeError):
        Distance**1.2

    with pytest.raises(TypeError):
        Distance**0

    assert Distance**-1 == 1 / Distance

    with pytest.raises(TypeError):
        2 / Distance

    with pytest.raises(TypeError):
        2 * Distance


@given(s.floats(allow_nan=False) | s.integers())
def test_any_magnitude(m):
    from xoutil.dim.app.standard import L
    assert float(m * L.metre) == float(m)


@given(s.floats(allow_nan=False, allow_infinity=False) | s.integers())
def test_any_magnitude_noinf(m):
    from xoutil.dim.app.standard import L
    from math import ceil, floor
    from six import integer_types
    Int = integer_types[-1]
    q = m * L.metre
    for f in (Int, float, abs, round, ceil, floor):
        assert f(q) == f(m)


def test_currencies():
    from xoutil.dim.app.currencies import Rate, Valuation, currency
    dollar = USD = currency('USD')
    euro = EUR = currency('EUR')
    rate = 1.19196 * USD / EUR

    assert isinstance(dollar, Valuation)
    assert isinstance(rate, Rate)

    # Even 0 dollars are a valuation
    assert isinstance(dollar - dollar, Valuation)

    # But 1 is not a value nor a rate
    assert not isinstance(dollar / dollar, Valuation)
    assert not isinstance(dollar / dollar, Rate)

    assert currency('a') is currency('A')

    with pytest.raises(TypeError):
        dollar + euro
