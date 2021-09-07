#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import pytest
from hypothesis import given, strategies as s

from xotl.tools.dim.meta import Signature, Quantity, Dimension, Scalar, UNIT


# A reasonable exponent.  We won't be dealing with universes of 100s
# dimensions.
exponents = s.integers(min_value=1, max_value=10)
signatures = s.text(alphabet="abcdefghijok", min_size=0, max_size=10)


def test_usage():
    @Dimension.new
    class L:
        metre = UNIT
        kilometre = 1000 * metre

    @Dimension.new
    class T:
        second = UNIT

    m, km = L.metre, L.kilometre
    s = T.second

    assert isinstance(m, L)
    assert not isinstance(1, L)
    assert isinstance(s, T)

    assert -km == -1 * km == -(1000 * m)
    assert +km == km

    Speed = L / T

    assert isinstance(m / s, Speed)
    assert not isinstance(m, T)

    assert hasattr(L / T, "metre_per_second")

    assert 10 * km == 10000 * m
    assert m < km

    with pytest.raises(TypeError):
        10 + 10 * km

    with pytest.raises(TypeError):
        m + s

    assert Speed.metre_per_second == m / s

    Acceleration = L / (T * T)
    assert hasattr(Acceleration, "metre_per_second_squared")
    # however:
    Not_Acceleration = L / T * T
    assert hasattr(Not_Acceleration, "metre_per_second_second")
    assert L == Not_Acceleration, "It is the same as Length"


def test_effort():
    @Dimension.new
    class Workforce:
        men = UNIT

    @Dimension.new
    class Time:
        second = UNIT

    class Effort(Workforce * Time):
        # Since the canonical unit of a composed quantity type is built from
        # the canonical units of the operands, but the true "canonical type"
        # of effort is usually men-hour we re-introduce it.
        men_hour = 60

    assert Effort.men_hour > Effort.men_second


def test_scalar_downgrade():
    from xotl.tools.dim.base import L

    km = L.km
    assert not isinstance(km / km, Quantity)
    assert km / km == 1
    assert not isinstance(km // km, Quantity)
    assert km // km == 1

    assert not isinstance(1 / km * km, Quantity)
    assert float(1 / km * km)


def test_natural_downgrade():
    from xotl.tools.dim.base import L

    km, cm = L.km, L.cm
    assert float(km) == 1000
    assert int(cm) == 0


def test_decimals():
    import decimal
    from xotl.tools.dim.base import m

    with pytest.raises(TypeError):
        third = decimal.Decimal("0.33") * m
        assert third < m


def test_signatures():
    distance = Signature("m")
    time = Signature("s")
    freq = 1 / time
    speed = distance / time
    acceleration = speed / time
    assert acceleration == distance / (time * Signature("s"))
    assert speed == distance * freq
    assert speed ** 3 == speed * speed * speed
    assert speed ** 0 == Signature() == speed / speed
    assert speed ** -3 == 1 / (speed ** 3)


@given(signatures, signatures)
def test_signatures_are_always_simplified(top, bottom):
    s = Signature(top, bottom)
    assert all(t not in s.bottom for t in s.top)
    assert all(b not in s.top for b in s.bottom)
    r = Signature(bottom, top)
    assert s.top == r.bottom and s.bottom == r.top

    s2 = Signature(top + bottom, bottom)
    assert s2 == Signature(top, None)
    s3 = Signature(top, top + bottom)
    assert s3 == Signature(None, bottom)


def test_quantity_math():
    metre = m = Quantity(1, Signature("m"))
    second = Quantity(1, Signature("s"))

    with pytest.raises(TypeError):
        metre < second

    assert metre < 2 * metre < (metre + 2 * metre)
    assert metre * metre == Quantity(1, Signature("mm"))
    assert metre / second == Quantity(1, Signature("m", "s"))
    assert metre * metre * metre == metre ** 3
    assert 1 / (metre * metre * metre) == metre ** -3

    assert 1000 * m % 3 == 1 * m
    assert 5 % (2 * m) == 1 / m
    assert 5 / (2 * m) == 2.5 / m

    with pytest.raises(TypeError):
        5 ** (2 * m)


def test_quantity_type_definitions():
    from xotl.tools.dim.base import Length, Time

    assert isinstance(Length, Dimension)
    assert isinstance(Time, Dimension)
    assert isinstance(Length / Time, Dimension)
    assert isinstance(Length ** 2, Dimension)
    assert Length * Length == Length ** 2

    assert Time / Time == Scalar
    assert Time / Time * Time == Time

    with pytest.raises(TypeError):
        Length + Time

    with pytest.raises(TypeError):
        Length - Time

    assert Length ** 1 is Length

    with pytest.raises(TypeError):
        Length ** 1.2

    assert Length ** 0 == Scalar
    assert Length ** -1 == 1 / Length

    with pytest.raises(TypeError):
        2 / Length

    with pytest.raises(TypeError):
        2 * Length


@given(exponents, exponents)
def test_general_power_rules(n, m):
    from xotl.tools.dim.base import L

    assert L ** n / L ** m == L ** (n - m)


@given(s.floats(allow_nan=False) | s.integers())
def test_any_magnitude(m):
    from xotl.tools.dim.base import L

    assert float(m * L.metre) == float(m)


@given(s.floats(allow_nan=False, allow_infinity=False) | s.integers())
def test_any_magnitude_noinf(m):
    from xotl.tools.dim.base import L
    from math import ceil, floor

    Int = int
    q = m * L.metre
    for f in (Int, float, abs, round, ceil, floor):
        assert f(q) == f(m)


def test_currencies():
    from xotl.tools.dim.currencies import Rate, Valuation, currency

    dollar = USD = currency("USD")
    euro = EUR = currency("EUR")
    rate = 1.19196 * USD / EUR

    assert isinstance(dollar, Valuation)
    assert isinstance(rate, Rate)

    # Even 0 dollars are a valuation
    assert isinstance(dollar - dollar, Valuation)

    # But 1 is not a value nor a rate
    assert not isinstance(dollar / dollar, Valuation)
    assert not isinstance(dollar / dollar, Rate)

    assert currency("a") is currency("A")

    with pytest.raises(TypeError):
        dollar + euro


def test_undistinguishable_definitions():
    from xotl.tools.dim.base import L

    @Dimension.new
    class Length:
        metre = UNIT

    assert L.metre == Length.metre

    # This is won't be be the same as L, not Length from above

    @Dimension.new
    class Length:
        km = UNIT

    assert L.metre != Length.km
    with pytest.raises(TypeError):
        L.metre < Length.km


def test_bug_30():
    from xotl.tools.dim.meta import Dimension, UNIT

    @Dimension.new
    class L:
        m = UNIT

    with pytest.raises(TypeError):

        class LL(L):
            mm = UNIT


def test_custom_quantity():
    class NewQuantity(Quantity):
        pass

    class NewDim(Dimension):
        Quantity = NewQuantity

    @NewDim.new
    class Length:
        m = UNIT

    m = Length.m
    Area = Length ** 2

    assert isinstance(m, NewQuantity)
    assert isinstance(1000 * m, NewQuantity)
    assert isinstance(Area._unit_, NewQuantity)

    @Dimension.new(Quantity=NewQuantity)
    class Time:
        s = UNIT

    Freq = 1 / Time
    assert isinstance(Time.s, NewQuantity)
    assert isinstance(Freq._unit_, NewQuantity)

    @NewDim.new(Quantity=Quantity)
    class Time:
        s = UNIT

    Freq = 1 / Time
    assert not isinstance(Time.s, NewQuantity)
    assert isinstance(Time.s, Quantity)
    assert not isinstance(Freq._unit_, NewQuantity)
    assert isinstance(Freq._unit_, Quantity)
