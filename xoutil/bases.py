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


from xoutil.names import strlist as strs
__all__ = strs('B32', 'B64')
del strs


class BaseConvertor(object):
    '''Base class that implements conversion algorithms based on a simple
    lookup table and a bit mask.

    It's supposed that the mask is a sigle string of set-up bits. And the table
    should be of length 2**<bit-lenght>.

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
    table = '0123456789abcdefghijklmnoprstuvw'
    mask = 0b11111
    case_insensitive = True


class B64(BaseConvertor):
    '''Handles [a kind of] base 64 conversions.

    This **is not standard base64**, but a reference-friendly base 64 to help
    the use case of generating a short reference.

    In base 64, each 6-bits chunks are represented by a single "digit". Digits
    comprises all 0..9, a..z, A..Z and the four symbols: `()[]`.

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
