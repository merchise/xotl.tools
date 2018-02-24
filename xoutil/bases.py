#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Integer encoding and decoding in different bases.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

_DEFAULT_TABLE = ("0123456789"
                  "abcdefghijklmnopqrstuvwxyz"
                  "ABCDEFGHIJKLMNOPQRSTUVWXYZ")

_MAX_BASE = len(_DEFAULT_TABLE)

_DEFAULT_BASE = _MAX_BASE


def _check_base(base):
    '''Check a base to be used in string to integer conversions.

    Return a tuple (base, table) if valid or raise an exception.

    '''
    from xoutil.eight import integer_types, string_types
    if isinstance(base, integer_types):
        table = _DEFAULT_TABLE
        if not (1 < base <= _MAX_BASE):
            raise ValueError('`base` must be between 2 and %s' % _MAX_BASE)
    elif isinstance(base, string_types):
        table = base
        base = len(table)
    else:
        from xoutil.eight import type_name
        msg = ('`base` must be an integer (base) or a string (table) with '
               'length greater or equal to 2; %s "%s" given')
        raise TypeError(msg % (type_name(base), base))
    return base, table


def int2str(number, base=_DEFAULT_BASE):
    '''Return the string representation of an integer using a base.

    :param base: The base.
    :type base: Either an integer or a string with a custom table.

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

    :param base: The base.
    :type base: Either an integer or a string with a custom table.

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
    return sign * res


class BaseConvertor(object):
    '''Base class that implements conversion algorithms based on a simple
    lookup table and a bit mask.

    Derived classes *must* provide a `table` attribute with the table of
    digits to use.

    '''
    @classmethod
    def inttobase(cls, num):
        '''Converts an integer to a base representation using the class' table.

        '''
        return int2str(num, base=cls.table)

    @classmethod
    def basetoint(cls, istr):
        '''Converts a base representation to a integer using the class' table.

        '''
        table = cls.table
        if cls.case_insensitive:
            table = table.lower()
        return str2int(istr, base=table)


class B32(BaseConvertor):
    '''Handles base-32 conversions.

    In base 32, each 5-bits chunks are represented by a single "digit". Digits
    comprises all symbols in 0..9 and a..v.

        >>> B32.inttobase(32) == '10'
        True

        >>> B32.basetoint('10')
        32

    '''
    table = '0123456789abcdefghijklmnopqrstuv'
    case_insensitive = True


class B64(BaseConvertor):
    '''Handles [a kind of] base 64 conversions.

    This **is not standard base64**, but a reference-friendly base 64 to help
    the use case of generating a short reference.

    In base 64, each 6-bits chunks are represented by a single "digit".
    Digits comprises all symbols in 0..9, a..z, A..Z and the three symbols:
    `()[`.

        >>> B64.inttobase(64) == '10'
        True

        >>> B64.basetoint('10')
        64

   .. warning::

      In this base, letters **are** case sensitive::

          >>> B64.basetoint('a')
          10

          >>> B64.basetoint('A')
          36

    '''
    table = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXZ()['
    case_insensitive = False


class B64symbolic(B64):
    '''Same as B64 but uses no capital letters and lots of symbols.'''
    table = '0123456789abcdefghijklmnopqrstuvwxyz:;><,._=!@#$^*/?\{}%`|"()[~\''
    case_insensitive = True
