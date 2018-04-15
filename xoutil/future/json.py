#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Extensions to the `json` standard library module.

It just adds the ability to encode/decode datetimes. But you should use the
JSONEncoder yourself.

You may use this module as drop-in replacement to Python's `json`.  Also it
contains definitions to use C library JSON speedups or Python replacements in
case that library is not installed in your system.

'''

# TODO: consider use IoC to extend python json module

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

from json import *    # noqa
import json as _stdlib    # noqa

from json import __all__    # noqa
__all__ = list(__all__) + ['file_load', 'encode_string']

from json import encoder, decoder    # noqa


class JSONEncoder(_stdlib.JSONEncoder):
    __doc__ = (_stdlib.JSONEncoder.__doc__ + '''
    Xoutil extends this class by supporting the following data-types:

    - `datetime`, `date` and `time` values, which are translated to strings
      using ISO format.

    - `Decimal` values, which are represented as a string representation.

    - Iterables, which are represented as lists.

    ''')
    DATE_FORMAT = str("%Y-%m-%d")
    TIME_FORMAT = str("%H:%M:%S")
    DT_FORMAT = str("%s %s") % (DATE_FORMAT, TIME_FORMAT)

    def default(self, obj):
        from datetime import datetime, date, time
        from decimal import Decimal
        from collections import Iterable
        from xoutil.future.datetime import assure
        if isinstance(obj, datetime):
            return assure(obj).strftime(self.DT_FORMAT)
        elif isinstance(obj, date):
            return assure(obj).strftime(self.DATE_FORMAT)
        elif isinstance(obj, time):
            return obj.strftime(self.TIME_FORMAT)
        elif isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, Iterable):
            return list(iter(obj))
        return super().default(obj)


try:
    JSONDecodeError    # noqa
except NameError:
    # Python 2 implementation raises 'ValueError'
    JSONDecodeError = ValueError


def file_load(filename):
    with file(filename, 'r') as f:
        return load(f)    # noqa


# --- encode strings ---

from json.encoder import encode_basestring    # noqa

try:
    from _json import encode_basestring_ascii
except ImportError:
    from json.encoder import (py_encode_basestring_ascii as    # noqa
                              encode_basestring_ascii)


def encode_string(string, ensure_ascii=True):
    '''Return a JSON representation of a Python string.

     :param ensure_ascii: If True, the output is guaranteed to be of type
         `str` with all incoming non-ASCII characters escaped.  If False, the
         output can contain non-ASCII characters.

    '''
    encode = encode_basestring_ascii if ensure_ascii else encode_basestring
    return encode(string)
