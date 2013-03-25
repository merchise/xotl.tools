#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.bases
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
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
__date__   = "Mon Mar 25 14:38:12 2013"


class BaseConvertor(object):
    '''Base class that implements convertion algorithms based on a simple
    lookup table and a bit mask.

    It's supposed that the mask is a sigle string of set-up bits. And the table
    should be of length 2**<bit-lenght>.

    Derived classes *must* provide a `table` and `mask` attributes with those
    values.

    '''
    @classmethod
    def inttobase(cls, num):
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
        mask = cls.mask
        bl = mask.bit_length()
        table = cls.table
        assert mask and table
        istr = istr.lstrip('0')
        if istr == '':
            return 0
        result = 0
        for symbol in istr:
            index = table.find(symbol)
            result = (result << bl) | index
        return result


class B32(BaseConvertor):
    '''Handles base-32 convertions.

        >>> B32.inttobase(32) == '10'
        True

        >>> B32.basetoint('10')
        32

    '''
    table = '0123456789abcdefghijklmnoprstuvw'
    mask = 0b11111


class B64(BaseConvertor):
    '''Handles Ref-Base-64 convertions.

    This is not standard base64, but a reference-friendly base 64 to help the
    use case of generating a short reference.

        >>> B64.inttobase(64) == '10'
        True

        >>> B64.basetoint('10')
        64

    '''
    table = '0123456789abcdefghijklmnopqrstuwxyzABCDEFGHIJKLMNOPQRSTUVWXZ()[]'
    mask = 0b111111
