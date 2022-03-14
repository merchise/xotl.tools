# flake8: noqa

import numbers

from .meta import Dimension, Quantity

class Length(metaclass=Dimension):
    m: Quantity
    metre: Quantity
    meter: Quantity
    km: Quantity
    kilometer: Quantity
    kilometre: Quantity
    mm: Quantity
    centimetre: Quantity
    centimeter: Quantity
    cm: Quantity
    millimeter: Quantity
    millimetre: Quantity
    nm: Quantity
    nanometer: Quantity
    nanometre: Quantity

L = Length

class Time(metaclass=Dimension):
    s: Quantity
    second: Quantity
    ms: Quantity
    millisecond: Quantity
    ns: Quantity
    nanosecond: Quantity
    minute: Quantity
    hour: Quantity

T = Time

class Mass(metaclass=Dimension):
    kg: Quantity
    kilogram: Quantity
    gram: Quantity

M = Mass

class ElectricCurrent(metaclass=Dimension):
    A: Quantity
    ampere: Quantity
    milliampere: Quantity

I = ElectricCurrent

class Temperature(metaclass=Dimension):
    K: Quantity
    kelvin: Quantity
    @classmethod
    def from_celcius(cls, val: numbers.Real) -> Quantity: ...
    @classmethod
    def from_fahrenheit(cls, val: numbers.Real) -> Quantity: ...

O = Temperature

class Substance(metaclass=Dimension):
    mol: Quantity
    mole: Quantity

N = Substance

class Luminosity(metaclass=Dimension):
    candela: Quantity

J = Luminosity

class Area(metaclass=Dimension):
    metre_squared: Quantity
    meter_squared: Quantity

class Volumen(metaclass=Dimension):
    metre_cubic: Quantity
    meter_cubic: Quantity

class Frequency(metaclass=Dimension):
    unit_per_second: Quantity
    Hz: Quantity

class Force(metaclass=Dimension):
    metre_kilogram_per_second_squared: Quantity
    meter_kilogram_per_second_squared: Quantity
    N: Quantity
    Newton: Quantity

class Pressure(metaclass=Dimension):
    kilogram_per_metre_per_second_squared: Quantity
    Pascal: Quantity
    Pa: Quantity
    bar: Quantity

class Velocity(metaclass=Dimension):
    meter_per_second: Quantity
    metre_per_second: Quantity

class Acceleration(metaclass=Dimension):
    meter_per_second_squared: Quantity
    metre_per_second_squared: Quantity
