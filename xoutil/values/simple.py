#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.values.simple
# ---------------------------------------------------------------------
# Copyright (c) 2015, 2016 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-08-26

'''Simple or internal coercers.

With coercers defined in this module, many of the `xoutil.string` utilities
could be deprecated.

In Python 3, all arrays, not only those containing valid byte or unicode
chars, are buffers.


'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.cl.simple import (name_coerce, decode_coerce,    # noqa
                              encode_coerce, unicode_coerce, bytes_coerce,
                              str_coerce, ascii_coerce, ascii_set_coerce,
                              lower_ascii_coerce, lower_ascii_set_coerce,
                              chars_coerce)


# TODO: Declared in 'xoutil.values.simple' at release 1.7 but not here in
# release 1.7.2:
# - strict_iterable_coerce
# - class text


def strict_iterable_coerce(arg):
    '''Return the same argument if it is a strict iterable.

    Strings are excluded.

    '''
    from xoutil.eight import string_types
    from collections import Iterable
    from . import Invalid
    ok = not isinstance(arg, string_types) and isinstance(arg, Iterable)
    return arg if ok else Invalid
