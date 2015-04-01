# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.json
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# Copyright (c) 2011, 2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Jul 1, 2011

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
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from xoutil.modules import copy_members as _copy_python_module_members
_pm = _copy_python_module_members()

load = _pm.load

from xoutil.names import strlist as strs
__all__ = strs('file_load')
__all__.extend(getattr(_pm, '__all__', dir(_pm)))
del strs, _copy_python_module_members


class JSONEncoder(_pm.JSONEncoder):
    __doc__ = (_pm.JSONEncoder.__doc__ + '''
    We also support:

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
        from xoutil.types import is_iterable
        from xoutil.datetime import assure
        if isinstance(obj, datetime):
            return assure(obj).strftime(self.DT_FORMAT)
        elif isinstance(obj, date):
            return assure(obj).strftime(self.DATE_FORMAT)
        elif isinstance(obj, time):
            return obj.strftime(self.TIME_FORMAT)
        elif isinstance(obj, Decimal):
            return str(obj)
        elif is_iterable(obj):
            return list(iter(obj))
        return super(JSONEncoder, self).default(obj)


def file_load(filename):
    with file(filename, 'r') as f:
        return load(f)


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


del _pm
