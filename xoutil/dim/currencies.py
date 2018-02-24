#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Concrete numbers for money.

You may have 10 dollars and 5 euros in your wallet, that does not mean that
you have 15 of anything (but bills, perhaps).  Though you may *evaluate* your
cash in any other currency you don't have that value until you perform an
exchange with a given rate.

This module support the family of currencies.  Usage::

  >>> from xoutil.dim.currencies import Rate, Valuation, currency
  >>> dollar = USD = currency('USD')
  >>> euro = EUR = currency('EUR')
  >>> rate = 1.19196 * USD/EUR

  >>> isinstance(dollar, Valuation)
  True

  >>> isinstance(rate, Rate)
  True

  # Even 0 dollars are a valuation
  >>> isinstance(dollar - dollar, Valuation)
  True

  # But 1 is not a value nor a rate
  >>> isinstance(dollar/dollar, Valuation) or isinstance(dollar/dollar, Rate)
  False


Currency names are case-insensitive.  We don't check the currency name is
listed in `ISO 4217`_.  So currency ``MVA`` is totally acceptable in this
module.

We don't download rates from any source.

This module allows you to trust your computations of money by allowing only
sensible operations::

  >>> dollar + euro  # doctest: +ELLIPSIS
  Traceback (...)
  ...
  OperandTypeError: unsupported operand type(s) for +: '{USD}/{}' and '{EUR}/{}


If you convert your euros to dollars::

  >>> dollar + rate * euro
  2.19196::{USD}/{}

  # Or your dollars to euros
  >>> dollar/rate + euro
  1.83895432733::{EUR}/{}


.. _ISO 4217: https://en.wikipedia.org/wiki/ISO_4217

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.eight.meta import metaclass


class ValueType(type):
    def __instancecheck__(self, which):
        from .meta import Quantity
        if isinstance(which, Quantity):
            return any(
                which.signature is currency.signature
                for currency in _Currency.units.values()
            )
        else:
            return False


class Valuation(metaclass(ValueType)):
    pass


class RateType(type):
    def __instancecheck__(self, which):
        from .meta import Quantity
        if isinstance(which, Quantity):
            top, bottom = which.signature.top, which.signature.bottom
            if len(top) == len(bottom) == 1:
                iscurrency = lambda s: isinstance(s[0], _Currency)
                return iscurrency(top) and iscurrency(bottom)
            else:
                return False
        else:
            return False


class Rate(metaclass(RateType)):
    pass


class _Currency(object):
    instances = {}
    units = {}

    def __new__(cls, name):
        from .meta import Quantity, Signature
        name = name.upper()
        res = cls.instances.get(name, None)
        if res is None:
            res = super(_Currency, cls).__new__(cls)
            res.name = name
            cls.instances[name] = res
            cls.units[name] = Quantity(1, Signature(top=(res, )))
        return res

    def __str__(self):
        return self.name

    @property
    def unit(self):
        return self.units[self.name]


def currency(name):
    '''Get the canonical value for the given currency `name`.

    '''
    return _Currency(name).unit
