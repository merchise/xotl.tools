import numbers

from .meta import Dimension, Quantity

class Length:
    m: Quantity
    metre: Quantity
    km: Quantity
    kilometer: Quantity
    mm: Quantity
    millimeter: Quantity
    nm: Quantity
    nanometer: Quantity

L = Length

class Time:
    s: Quantity
    second: Quantity
    ms: Quantity
    millisecond: Quantity
    ns: Quantity
    nanosecond: Quantity
    minute: Quantity
    hour: Quantity

T = Time

class Mass:
    kg: Quantity
    kilogram: Quantity
    gram: Quantity

M = Mass

class ElectricCurrent:
    A: Quantity
    ampere: Quantity
    milliampere: Quantity

I = ElectricCurrent

class Temperature:
    K: Quantity
    kelvin: Quantity
    @classmethod
    def from_celcius(cls, val: numbers.Real) -> Quantity: ...
    @classmethod
    def from_fahrenheit(cls, val: numbers.Real) -> Quantity: ...

O = Temperature

class Substance:
    mol: Quantity
    mole: Quantity

N = Substance

class Luminosity:
    candela: Quantity

J = Luminosity

Area: Dimension
Volumen: Dimension

Frequency: Dimension
Force: Dimension

Pressure: Dimension
Presure: Dimension

Velocity: Dimension
Acceleration: Dimension
