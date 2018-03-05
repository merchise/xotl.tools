#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Facilities to work with `concrete numbers`_.

   A concrete number is a number associated with the things being counted, in
   contrast to an abstract number which is a number as a single entity.

   -- Wikipedia__


__ `concrete numbers`_
.. _concrete numbers: https://en.wikipedia.org/wiki/Concrete_number


This module allows you to define dimensions (or quantity types):

   >>> from xoutil.dim.meta import Dimension, UNIT
   >>> @Dimension.new
   ... class Length(object):
   ...     metre = UNIT
   ...     kilometre = 1000 * metre
   ...     centimetre = metre/100
   ...     milimetre = milimetres = metre/1000
   ...
   ...     inch = inches = 24.5 * milimetres
   ...     foot = feet = 12 * inches


.. seealso:: Module `~xoutil.dim.base`:mod: defines the standard base
   quantities.


Each dimension **must** define a single *canonical unit* for measuring
quantities within the dimension.  Values in the dimension are always expressed
in terms of the canonical units.

In the previous example the dimension Length defined the `metre` for its
canonical unit.  The name of canonical unit defines the `signature
<Signature>`:class: for the quantities in the dimension.

When printed (or ``repr``-ed) `quantities <Quantity>`:class: use the format
``<magnitude>::<signature>``:

   >>> metre = Length.metre
   >>> metre
   1::{<Length.metre>}/{}

Quantities support the standard arithmetical operations of addition,
subtraction, multiplication and division.  In fact, you obtain different
quantities in the dimension by multiplying with the canonical unit:

   >>> metre + metre
   2::{<Length.metre>}/{}

   >>> metre*metre
   1::{<Length.metre>, <Length.metre>}/{}

   >>> km = 1000 * metre

   >>> 5 * km
   5000::{<Length.metre>}/{}

`Dimensional homogeneity`__ imposes restrictions on the allowed operations
between quantities.  Only commensurable quantities (quantities of the same
dimension) can be compared, equated, added, or subtracted.

__ https://en.wikipedia.org/wiki/Dimensional_analysis#Dimensional_homogeneity

   >>> @Dimension.new
   >>> class Time(object):
   ...     second = UNIT

   >>> metre + Time.second  # doctest: +ELLIPSIS
   Traceback (...)
   ...
   OperandTypeError: unsupported operand type(s) for +:...


However, you can take ratios of incommensurable quantities (quantities with
different dimensions), and multiply or divide them.

    >>> metre/Time.second
    >>> 1::{<Length.metre>}/{<Time.second>}


.. warning:: `Decimal numbers <decimal.Decimal>`:py:class: are not supported.

   This module makes not attempt to fix the standing incompatibility between
   floats and `decimal.Decimal`:py:class:\ :

      >>> import decimal
      >>> decimal.Decimal('0') + 0.1  # doctest: +ELLIPSIS
      Traceback (...)
      ...
      TypeError: unsupported operand type(s) for +: 'Decimal' and 'float'


The signature created by `Dimension`:class: for its canonical unit is simply a
string that varies with the name of the dimension and that of the canonical
unit.  This implies that you can *recreate* the same dimension and it will be
interoperable with the former::

   >>> @Dimension.new
   ... class L(object):
   ...    m = UNIT

   >>> m = L.m  # Save this


   >>> # Recreate the same dimension.
   >>> @Dimension.new
   ... class L(object):
   ...    m = UNIT

   >>> m == L.m
   True

Both the dimension name and the canonical unit name *must* be the same for
this to work.

.. note:: We advice to define a dimension only once and import it where
   needed.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import functools
import numbers
from xoutil.eight.meta import metaclass


#: The unit for any kind of quantity.
UNIT = 1


class Dimension(type):
    '''A type for `quantities`_.

    This is a metaclass for dimensions.  Every instance (class) will
    automatically have the following attributes:

    .. attribute:: _unitname_

       The name of canonical unit in the dimension.  Notice that `aliases
       <new>`:meth: are created after the defined canonical unit.  This is the
       name of the attribute provided in the class definition of the dimension
       with value equal to `UNIT`:const:.

    .. attribute:: _unit_

       The canonical `quantity <Quantity>`:class:.  This is the quantity 1
       (`UNIT`:const:) expressed in terms of the canonical unit.

    .. attribute:: _signature_

       The canonical `signature <Signature>`:class: of the quantities.

    It's always true that ``Quantity(UNIT, self._signature_) == self._unit_``.

    .. _quantities: https://en.wikipedia.org/wiki/Concrete_numbers

    The provided dimension `~xoutil.dim.base.Length`:class: has the canonical
    quantity `1 metre`::

      >>> Length.metre
      1::{<Length.metre>}/{}

      >>> Length._unit_ == Length.metre == Quantity(1, Length._signature_)
      True

    '''
    def __new__(cls, name, bases, attrs):
        wrappedattrs = {}
        Base = next((base for base in bases if isinstance(base, cls)), None)
        if Base is not None:
            unit = Base._unitname_
            signature = Base._signature_
        else:
            unit = None
            signature = Signature()
        for attr, val in attrs.items():
            if isinstance(val, BareReal):
                if val == UNIT and unit is not None:
                    raise TypeError('quantity with multiple units')
                if unit is None and val == UNIT:
                    unit = attr
                    assert not signature.top
                    signature.top = ('<{}.{}>'.format(name, unit), )
                    # WARNING: In order to make a single looping structure we
                    # intentionally break the signature immutability
                wrappedattrs[attr] = Quantity(val, signature)
            else:
                if unit is None and isinstance(val, Quantity):
                    # This is the case when I need to create the quantity from
                    # operations.  It's is not a public API.  We also break
                    # the signature immutability here.
                    if val.magnitude == UNIT:
                        unit = attr
                    assert not signature.top and not signature.bottom
                    signature.top = val.signature.top
                    signature.bottom = val.signature.bottom
                wrappedattrs[attr] = val
        if unit is None:
            raise TypeError('dimension without a unit')
        self = super(Dimension, cls).__new__(
            cls, name, bases, wrappedattrs
        )
        self._unitname_ = unit
        self._unit_ = getattr(self, unit)
        self._signature_ = signature
        return self

    @classmethod
    def new(cls, *source, **kwargs):
        '''Define a new dimension.

        This is a wrapped decorator.  The actual possible signatures are:

           - ``new(unit_alias=None, unit_aliases=None)(source)``

           - ``new(source)``

        This allows to use this method as decorator with or without arguments.

        :param source: A class with at least the canonical unit definition.
                       Other unit definitions will be automatically converted.

        :keyword unit_alias: An alias for the canonical unit.  You cannot use
                             a `source` with several canonical units.  This is
                             a simple way to introduce a single alias.

        :keyword unit_aliases: A sequence with the name of other aliases for
                               the canonical unit.

        Example:

           >>> @Dimension.new(unit_alias='man')
           ... class Workforce(object):
           ...    men = UNIT

           >>> Workforce.men == Workforce.man == Workforce._unit_
           True

        The resulting class will be an instance of `Dimension`:class::

           >>> isinstance(Workforce, Dimension)
           True

        The original class is totally missed:

           >>> Workforce.mro()
           [...Workforce, object]

        To complete the example, let's introduce the dimension Effort that
        expresses the usual amount of men-power and time needed to complete
        some task.  However `~xoutil.dim.base.Time`:class: has the second as
        it canonical unit, but the standard for Effort is men-hour:

           >>> class Effort(Workforce * Time):
           ...    # Since the canonical unit of a composed quantity type is
           ...    # built from the canonical units of the operands, but the
           ...    # true "canonical type" of effort is usually men-hour we
           ...    # re-introduce it.
           ...    men_hour = 60

        This does not mean that ``Effort._unit_ == Effort.men_hour``.  The
        canonical unit would be ``Effort.men_second``.

        '''
        from xoutil.decorator.meta import decorator

        @decorator
        def _new(source, unit_alias=None, unit_aliases=None):
            from xoutil.objects import copy_class
            res = copy_class(source, meta=cls)
            if unit_alias:
                setattr(res, unit_alias, res._unit_)
            if unit_aliases:
                for alias in unit_aliases:
                    setattr(res, alias, res._unit_)
            return res
        if source and kwargs or len(source) > 1:
            raise TypeError('Invalid signature')
        return _new(*source, **kwargs)

    def __instancecheck__(self, instance):
        if isinstance(instance, Quantity):
            return instance.signature == self._signature_
        else:
            return False

    def __mul__(self, other):
        if isinstance(other, Dimension):
            name = TIMES(self.__name__, other.__name__)
            if self == other:
                unit = SQUARED(self._unitname_)
                quant = Quantity(UNIT, self._signature_**2)
            else:
                unit = TIMES(self._unitname_, other._unitname_)
                quant = Quantity(
                    UNIT, self._signature_ * other._signature_
                )
            klass = type(self)
            return klass(name, (object, ), {unit: quant})
        else:
            raise OperandTypeError('*', self, other)

    def __pow__(self, exp):
        if isinstance(exp, numbers.Integral):
            if exp == 0:
                return Scalar
            elif exp == 1:
                return self
            elif exp == 2:
                return self * self
            elif exp < 0:
                return 1 / (self**-exp)
            else:
                assert exp > 0
                name = POWER(self.__name__, exp)
                unit = POWER(self._unitname_, exp)
                quant = Quantity(UNIT, self._signature_**exp)
                klass = type(self)
                return klass(name, (object, ), {unit: quant})
        else:
            raise OperandTypeError('**', self, exp)

    def __div__(self, other):
        if isinstance(other, Dimension):
            if self == other:
                return Scalar
            else:
                name = PER(self.__name__, other.__name__)
                unit = PER(self._unitname_, other._unitname_)
                quant = Quantity(UNIT, self._signature_ / other._signature_)
                klass = type(self)
                return klass(name, (object, ), {unit: quant})
        else:
            raise OperandTypeError('/', self, other)
    __truediv__ = __floordiv__ = __div__

    def __rdiv__(self, numerator):
        assert not isinstance(numerator, Dimension)
        if numerator == 1:
            name = PER('unit', self.__name__)
            unit = PER('unit', self._unitname_)
            quant = Quantity(UNIT, 1 / self._signature_)
            klass = type(self)
            return klass(name, (object, ), {unit: quant})
        else:
            raise OperandTypeError('/', numerator, self)
    __rtruediv__ = __rfloordiv__ = __rdiv__

    def __eq__(self, other):
        if isinstance(other, Dimension):
            return self._signature_ == other._signature_
        else:
            raise TypeError(
                "incomparable types '%s' and '%s'" %
                (type(self).__name__, type(other).__name__)
            )


class Signature(object):
    '''The layout of the kinds that compose a quantity.

    The layout is given by a pair non-ordered collections (repetition
    is allowed): the numerator (we call it top within the signature)
    and the denominator (bottom).

    We represent a signature as ``{top elements}/{bottom elements}``.

    You may regard a signature as an abstract 'syntactical' part of a
    quantity.  For Length, the ``{metre}/{}`` is the signature of such a
    quantity.

    The number "10" is not tied to any particular kind of quantity.  Bare
    numbers have no kind and the bear the signature ``{}/{}``.

    The items of top and bottom are required to be comparable for equality
    (``==``).

    You can multiply and divide signatures and simplification happens
    automatically.

    You *should* regard signatures as immutable values.  In fact, this is kind
    of an internal, but interesting, concept of this module.

    Examples::

      >>> distance = Signature('m')
      >>> distance
      {m}/{}

      >>> time = Signature('s')

      >>> freq = 1/time
      >>> freq
      {}/{s}

      >>> speed = distance/time
      >>> speed
      {m}/{s}

      >>> acceleration = speed/time
      >>> acceleration
      {m}/{s, s}

    You may compare signatures for equality.

      >>> acceleration == distance/(time*Signature('s'))
      True

      >>> speed == distance * freq
      True

    Signature don't support neither addition nor subtraction::

      >>> distance + distance  # doctest: +ELLIPSIS
      Traceback (...)
      ...
      TypeError: unsupported operand type(s) for +: 'Signature' and 'Signature'

    '''
    __slots__ = ('top', 'bottom')

    def __init__(self, top=None, bottom=None):
        self.top, self.bottom = self.simplify(top, bottom)

    def __eq__(self, other):
        try:
            from xoutil.future.collections import Counter
        except ImportError:
            from xoutil.collections import Counter
        if isinstance(other, type(self)):
            return Counter(self.top) == Counter(other.top) and \
                Counter(self.bottom) == Counter(other.bottom)
        else:
            return False

    def __ne__(self, other):
        return not(self == other)

    __hash__ = None  # FIXME: Hash

    def __lt__(self, other):
        raise TypeError('signatures are not orderable')
    __gt__ = __ge__ = __le__ = __lt__

    def __mul__(self, other):
        cls = type(self)
        if other == UNIT:
            return self
        elif isinstance(other, cls):
            return cls(self.top + other.top, self.bottom + other.bottom)
        else:
            raise TypeError
    __rmul__ = __mul__

    def __div__(self, other):
        cls = type(self)
        if other == UNIT:
            return self
        elif isinstance(other, cls):
            return cls(self.top + other.bottom, self.bottom + other.top)
        else:
            raise TypeError
    __truediv__ = __floordiv__ = __div__

    def __rdiv__(self, numerator):
        if numerator == UNIT:
            cls = type(self)
            return cls(self.bottom, self.top)
        else:
            raise TypeError
    __rtruediv__ = __rfloordiv__ = __rdiv__

    def __pow__(self, exp):
        if isinstance(exp, numbers.Integral):
            if exp == 0:
                return Signature()
            elif exp > 0:
                return Signature(self.top * exp, self.bottom * exp)
            else:
                return Signature(self.bottom * -exp, self.top * -exp)
        else:
            raise TypeError

    @staticmethod
    def simplify(top, bottom):
        '''Removes equal items from top and bottom in a one-to-one
        correspondence.

        Signatures are simplified on initialization::

           >>> Signature('abcxa', 'bxay')
           {c, a}/{y}

        This function takes top and bottom and returns simplified
        tuples for top and bottom.

        '''
        top = [] if top is None else list(top)
        bottom = [] if bottom is None else list(bottom)
        i = 0
        while i < len(top):
            j = 0
            while j < len(bottom) and bottom[j] != top[i]:
                j += 1
            if j < len(bottom):
                assert bottom[j] == top[i]
                del bottom[j]
                del top[i]
            else:
                i += 1
        return tuple(top), tuple(bottom)

    def __str__(self):
        wrap = lambda s: '{{{0}}}'.format(s)
        top = wrap(', '.join(str(t) for t in self.top))
        bottom = wrap(', '.join(str(b) for b in self.bottom))
        return '{top}/{bottom}'.format(top=top, bottom=bottom)

    __repr__ = __str__


class _BareRealType(type):
    def __instancecheck__(self, i):
        return isinstance(i, numbers.Real) and not isinstance(i, Quantity)


class BareReal(metaclass(_BareRealType)):
    '''Any real that is not a Quantity instance.'''


@functools.total_ordering
class Quantity(numbers.Real):
    '''A concrete number of `quantity` (expressed in) `units`.

    .. seealso:: https://en.wikipedia.org/wiki/Concrete_number

    :param quantity: A real number.
    :param units: A `signature <Signature>`:class: for the units the
                  denominate the given quantity.

    You can construct instances by operating with the attributes of a
    dimension.  For instance, this is 5 kilometres:

       >>> from xoutil.dim.base import L
       >>> 5 * L.km
       5000::{<Length.metre>}/{}

    A concrete number is of the type of its dimension:

       >>> isinstance(5 * L.km, L)
       True

    '''
    __slots__ = ('magnitude', 'signature')

    def __init__(self, quantity, units):
        if not isinstance(quantity, BareReal):
            raise TypeError('Quantities must be real numbers')
        self.magnitude = quantity
        self.signature = units

    def __str__(self):
        return '{}::{}'.format(self.magnitude, self.signature)
    __repr__ = __str__

    def __neg__(self):
        return Quantity(-self.magnitude, self.signature)

    def __pos__(self):
        return Quantity(self.magnitude, self.signature)

    def __add__(self, other):
        if isinstance(other, Quantity) and self.signature == other.signature:
            return Quantity(self.magnitude + other.magnitude, self.signature)
        else:
            # What is the meaning of "10km + 1"?
            raise OperandTypeError('+', self, other)
    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Quantity) and self.signature == other.signature:
            return Quantity(self.magnitude - other.magnitude, self.signature)
        else:
            # What is the meaning of "10km - 1"?
            raise OperandTypeError('-', self, other)

    def __mul__(self, other):
        if isinstance(other, BareReal):
            other = Quantity(other, Signature())
        if isinstance(other, Quantity):
            return downgrade_to_scalar(
                Quantity(self.magnitude * other.magnitude,
                         self.signature * other.signature)
            )
        else:
            raise OperandTypeError('*', self, other)
    __rmul__ = __mul__

    def __pow__(self, exp):
        if isinstance(exp, numbers.Integral) and exp != 0:
            if exp < 0:
                return 1 / (self**(-exp))
            else:
                return Quantity(self.magnitude**exp, self.signature**exp)
        else:
            raise OperandTypeError('**', self, exp)

    def __div__(self, other):
        if isinstance(other, BareReal):
            other = Quantity(other, Signature())
        if isinstance(other, Quantity):
            return downgrade_to_scalar(
                Quantity(self.magnitude / other.magnitude,
                         self.signature / other.signature)
            )
        else:
            raise OperandTypeError('/', self, other)
    __truediv__ = __div__

    def __floordiv__(self, other):
        if isinstance(other, BareReal):
            other = Quantity(other, Signature())
        if isinstance(other, Quantity):
            return downgrade_to_scalar(
                Quantity(self.magnitude // other.magnitude,
                         self.signature / other.signature)
            )
        else:
            raise OperandTypeError('//', self, other)

    def __rdiv__(self, other):
        if isinstance(other, BareReal):
            other = Quantity(other, Signature())
            return downgrade_to_scalar(
                Quantity(other.magnitude / self.magnitude,
                         other.signature / self.signature)
            )
        else:
            raise OperandTypeError('/', other, self)
    __rtruediv__ = __rdiv__

    def __rfloordiv__(self, other):
        if isinstance(other, BareReal):
            other = Quantity(other, Signature())
            return downgrade_to_scalar(
                Quantity(other.magnitude // self.magnitude,
                         other.signature / self.signature)
            )
        else:
            raise OperandTypeError('//', other, self)

    def __eq__(self, other):
        if isinstance(other, BareReal) and self.signature == SCALAR:
            return self.magnitude == other
        elif isinstance(other, Quantity) and self.signature == other.signature:
            return self.magnitude == other.magnitude
        else:
            raise TypeError(
                'incomparable quantities: %r and %r' % (self, other)
            )

    def __lt__(self, other):
        if isinstance(other, Quantity) and self.signature == other.signature:
            return self.magnitude < other.magnitude
        else:
            raise TypeError(
                'incomparable quantities: %r and %r' % (self, other)
            )

    # The following make Quantity more compatible with numbers.Real.  In all
    # cases, taking a Quantity for a float takes the magnitude expressed in
    # the canonical unit.

    def __le__(self, other):
        if isinstance(other, Quantity) and self.signature == other.signature:
            return self.magnitude <= other.magnitude
        else:
            raise TypeError(
                'incomparable quantities: %r and %r' % (self, other)
            )

    def __float__(self):
        return float(self.magnitude)

    def __trunc__(self):
        return self.magnitude.__trunc__()

    def __abs__(self):
        return abs(self.magnitude)

    def __round__(self):
        return round(self.magnitude)

    def __ceil__(self):
        import math
        return math.ceil(self.magnitude)

    def __floor__(self):
        import math
        return math.floor(self.magnitude)

    def __mod__(self, other):
        if isinstance(other, BareReal):
            return Quantity(self.magnitude % other, self.signature)
        else:
            raise OperandTypeError('%', self, other)

    def __rmod__(self, other):
        # This is a rare operation.  Imagine: 5 % 2m to be 1/m....  But if I
        # can do 5/2m and that is 2.5/m, then % should be allowed.
        if isinstance(other, BareReal):
            return Quantity(other % self.magnitude, 1 / self.signature)
        else:
            raise OperandTypeError('%', self, other)

    def __rpow__(self, other):
        raise OperandTypeError('**', other, self)


SCALAR = Signature()


@Dimension.new
class Scalar(object):
    '''A quantity whose signature is always *empty*.

    Most of the time you should not deal with this quantity.  Any normal
    operation that results in a scalar gets reduced to Python's type:

        >>> from xoutil.dim.base import L
        >>> L.m/L.m
        1.0

    This type makes the operations on `dimensions <Dimension>`:class: closed
    under multiplication:

        >>> Scalar * L == L == L * Scalar
        True

    '''
    unit = Quantity(UNIT, SCALAR)


TIMES = lambda a, b: '{}_{}'.format(a, b)
PER = lambda a, b: '{}_per_{}'.format(a, b)
SQUARED = lambda a: '{}_squared'.format(a)


def POWER(a, e):
    return '{}_pow_{}'.format(a, e)


class OperandTypeError(TypeError):
    def __init__(self, operand, val1, val2):
        if isinstance(val1, Quantity):
            t1 = val1.signature
        else:
            t1 = type(val1).__name__
        if isinstance(val2, Quantity):
            t2 = val2.signature
        else:
            t2 = type(val2).__name__
        super(OperandTypeError, self).__init__(
            "unsupported operand type(s) for %s: '%s' and '%s'" %
            (operand, t1, t2)
        )


def downgrade_to_scalar(quantity):
    '''Downgrade a concrete number to a bare number if possible.

    .. note:: This is not an API of this module.

    '''
    if quantity.signature == SCALAR:
        return quantity.magnitude
    else:
        return quantity
