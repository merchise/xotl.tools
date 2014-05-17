#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.bases
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


__author__ = "Manuel Vázquez Acosta <mva.led@gmail.com>"
__date__ = "Mon Mar 25 14:38:12 2013"


try:
    _strs = basestring
except:
    _strs = str


_DEFAULT_TABLE = ("0123456789"
                  "abcdefghijklmnopqrstuvwxyz"
                  "ABCDEFGHIJKLMNOPQRSTUVWXYZ")

_MAX_BASE = len(_DEFAULT_TABLE)

_DEFAULT_BASE = _MAX_BASE


def _check_base(base):
    '''Check a base to be used in string to integer conversions.

    Return a tuple (base, table) if valid or raise an exception.

    '''
    if isinstance(base, (int, long)):
        table = _DEFAULT_TABLE
        if not (1 < base <= _MAX_BASE):
            raise ValueError('`base` must be between 2 and %s' % _MAX_BASE)
    elif isinstance(base, _strs):
        table = base
        base = len(table)
    else:
        msg = ('`base` must be an integer (base) or a string (table) with '
               'length greater or equal to 2; %s "%s" given')
        raise TypeError(msg % (type(base).__name__, base))
    return base, table


def int2str(number, base=_DEFAULT_BASE):
    '''Return the string representation of an integer using a base.

    `base` could be an integer or a string with a custom table.

    Examples::

      >>> int2str(65535, 16)
      'ffff'

      >>> int2str(65535)
      'h31'

      >>> int2str(65110208921, 'merchise')
      'ehimseiemsce'

      >>> int2str(651102, 2)
      '10011110111101011110'

    '''
    base, table = _check_base(base)
    sign = '' if number >= 0 else '-'
    number = abs(number)
    res = table[0] if number == 0 else ''
    while number:
        number, idx = divmod(number, base)
        res = table[idx] + res
    return str(sign + res)


def str2int(src, base=_DEFAULT_BASE):
    '''Return the integer decoded from a string representation using a base.

    `base` could be an integer or a string with a custom table.

    Examples::

      >>> str2int('ffff', 16)
      65535

      >>> str2int('1c', 16) == int('1c', 16)
      True

      >>> base = 'merchise'
      >>> number = 65110208921
      >>> str2int(int2str(number, base), base) == number
      False

      >>> base = 32
      >>> str2int(int2str(number, base), base) == number
      True

    '''
    base, table = _check_base(base)
    if src.startswith('-'):
        sign = -1
        i = 1
    else:
        sign = 1
        i = 0
    res = 0
    while i < len(src):
        res *= base
        res += table.index(src[i])
        i += 1
    return sign*res


class BaseConvertor(object):
    '''Base class that implements conversion algorithms based on a simple
    lookup table and a bit mask.

    It's supposed that the mask is a sigle string of set-up bits. And the
    table should be of length 2**<bit-lenght>.

    Derived classes *must* provide a `table` and `mask` attributes with those
    values.

    '''
    @classmethod
    def inttobase(cls, num):
        '''Converts an integer to a base representation using the class' table
        and mask attributes.

        '''
        mask = cls.mask
        bl = mask.bit_length()
        table = cls.table
        assert mask and table
        assert num >= 0
        if num == 0:
            return '0'
        digits = []
        while num > 0:
            digit = num & mask
            num = num >> bl
            digits.append(digit)
        return ''.join(table[digit] for digit in reversed(digits))

    @classmethod
    def basetoint(cls, istr):
        '''Converts a base representation to a integer using the class' table
        and mask attributes.

        '''
        mask = cls.mask
        bl = mask.bit_length()
        table = cls.table
        istr = istr.lstrip('0')
        if cls.case_insensitive:
            istr = istr.lower()
        if istr == '':
            return 0
        result = 0
        for symbol in istr:
            index = table.find(symbol)
            result = (result << bl) | index
        return result


class B32(BaseConvertor):
    '''Handles base-32 conversions.

    In base 32, each 5-bits chunks are represented by a single "digit". Digits
    comprises all 0..9 and a..w.

        >>> B32.inttobase(32) == '10'
        True

        >>> B32.basetoint('10')
        32

    '''
    table = '0123456789abcdefghijklmnopqrstuv'
    mask = 0b11111
    case_insensitive = True


class B64(BaseConvertor):
    '''Handles [a kind of] base 64 conversions.

    This **is not standard base64**, but a reference-friendly base 64 to help
    the use case of generating a short reference.

    In base 64, each 6-bits chunks are represented by a single "digit".
    Digits comprises all 0..9, a..z, A..Z and the four symbols: `()[]`.

        >>> B64.inttobase(64) == '10'
        True

        >>> B64.basetoint('10')
        64

   .. warning::

      In this base, letters **are** case sensitive::

          >>> B64.basetoint('a')
          10

          >>> B64.basetoint('A')
          35

    '''
    table = '0123456789abcdefghijklmnopqrstuwxyzABCDEFGHIJKLMNOPQRSTUVWXZ()[]'
    mask = 0b111111
    case_insensitive = False


class B64symbolic(B64):
    '''Same as B64 but uses no capital letters and lots of symbols.'''
    table = '0123456789abcdefghijklmnopqrstuwxyz:;><,.-_=+!@#$^*/?\{}%`|"()[]'
    case_insensitive = True
