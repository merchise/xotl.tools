#!/USSR/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# standard
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-09-14

'''The standard `physical quantities`_.

.. _physical quantities: https://en.wikipedia.org/wiki/International_System_of_Quantities#Base_quantities

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from ..meta import (
    QuantityType,
    UNIT,
)


def kilo(v):
    return 1000 * v


def centi(v):
    return v / 100


def milli(v):
    return v / 1000


def micro(v):
    return v / 1000000


def nano(v):
    return v / (10**9)


@QuantityType.new
class Length(object):
    'Length'
    metre = UNIT
    kilometer = km = kilo(metre)
    centimeter = cm = centi(metre)
    millimeter = mm = milli(metre)
    nanometer = nm = nano(metre)


metre = m = Length.m = Length.metre
L = Length


@QuantityType.new
class Time(object):
    'Time'
    second = UNIT
    millisecond = milli(second)
    nanosecond = nano(second)
    minute = second * 60
    hour = minute * 60


second = s = Time.s = Time.second
T = Time


@QuantityType.new
class Mass(object):
    'Mass'
    kilogram = UNIT
    gram = kilogram / 1000


kilogram = kg = Mass.kg = Mass.kilogram
M = Mass


@QuantityType.new
class ElectricCurrent(object):
    'Electric Current'
    ampere = UNIT
    milliampere = milli(ampere)


A = ampere = ElectricCurrent.A = ElectricCurrent.ampere
I = ElectricCurrent


@QuantityType.new
class Temperature(object):
    'Thermodynamic temperature'
    kelvin = UNIT
    C = celcius = kelvin - 273.15
    F = fahrenheit = kelvin * (9 / 5) - 459.67


K = kelvin = Temperature.K = Temperature.kelvin
C = celcius = Temperature.C
O = Temperature   # The actual symbol would be the capital letter Theta: Θ


@QuantityType.new
class Substance(object):
    mole = UNIT


mol = Substance.mol = Substance.mole
N = Substance


@QuantityType.new
class Luminosity(object):
    'Luminous intensity'
    candela = UNIT


J = Luminosity


# Derived quantities
Area = L**2
Volume = L**3
Frequency = T**-1
Force = L * M * T**-2
Presure = L**-1 * M * T**-2
Velocity = L * T**-1
Acceleration = L * T**-2
