#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""The standard `physical quantities`_.

.. _physical quantities: \
https://en.wikipedia.org/wiki/International_System_of_Quantities#Base_quantities

"""

from .meta import UNIT, Dimension


def kilo(v):
    return 1000 * v


def centi(v):
    return v / 100


def milli(v):
    return v / 1000


def micro(v):
    return v / 1000000


def nano(v):
    return v / (10 ** 9)


@Dimension.new()
class Length:
    metre = UNIT
    kilometre = kilometer = km = kilo(metre)
    centimetre = centimeter = cm = centi(metre)
    millimetre = millimeter = mm = milli(metre)
    nanometre = nanometer = nm = nano(metre)


metre = m = Length.m = Length.meter = Length.metre
L = Length


@Dimension.new
class Time:
    second = UNIT
    millisecond = ms = milli(second)
    nanosecond = ns = nano(second)
    minute = second * 60
    hour = minute * 60


second = s = Time.s = Time.second
T = Time


@Dimension.new(unit_aliases=("kg",))
class Mass:
    kilogram = UNIT
    gram = kilogram / 1000


kilogram = kg = Mass.kg
M = Mass


@Dimension.new(unit_aliases="A")
class ElectricCurrent:
    ampere = UNIT
    milliampere = milli(ampere)


A = ampere = ElectricCurrent.A
I = ElectricCurrent


@Dimension.new(unit_aliases="K")
class Temperature:
    kelvin = UNIT

    @classmethod
    def from_celcius(cls, val):
        "Convert `val` ºC to K"
        return (val + 273.15) * cls.kelvin

    @classmethod
    def from_fahrenheit(cls, val):
        "Convert `val` ºF to K"
        return (val + 459.67) * (5 / 9) * cls.kelvin


K = kelvin = Temperature.K
O = Temperature  # The actual symbol would be the capital letter Theta: Θ


@Dimension.new(unit_alias="mol")
class Substance:
    mole = UNIT


mole = mol = Substance.mol
N = Substance


@Dimension.new
class Luminosity:
    candela = UNIT


J = Luminosity


# Derived quantities
Area = L ** 2
Volume = L ** 3
Volume.metre_cubic = Volume.meter_cubic = Volume._unit_
Volume._unitname_ = "metre_cubic"

Frequency = T ** -1
Frequency.Hz = Frequency._unit_

Force = L * M / T ** 2
assert hasattr(Force, "metre_kilogram_per_second_squared")
assert Force == L * M * T ** -2
Force.Newton = Force.N = Force.meter_kilogram_per_second_squared = Force._unit_

Pressure = Presure = M / L / T ** 2
assert hasattr(Pressure, "kilogram_per_metre_per_second_squared")
assert Pressure == L ** -1 * M * T ** -2, "as defined in Wikipedia"
Pressure.Pascal = Pressure.Pa = Pressure.kilogram_per_meter_per_second_squared = Pressure._unit_
Pressure.bar = 100000 * Pressure.Pa

Speed = Velocity = L / T
Velocity.meter_per_second = Velocity._unit_

Acceleration = L / T ** 2
Acceleration.meter_per_second_squared = Acceleration._unit_
