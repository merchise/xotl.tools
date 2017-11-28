#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''CSV parsing and writing Xoutil extensions.

This module is an extension of `csv`:mod: Python standard module, it provides
classes and tools that assist in the reading and writing of `Comma Separated
Value (CSV)`:abbr: files, and implements the interface described by PEP
`305`:pep:.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)


from csv import *    # noqa
import csv as _stdlib    # noqa


try:
    from csv import unix_dialect
except ImportError:
    # Not defined in Python 2
    class unix_dialect(Dialect):    # noqa
        '''Describe the usual properties of Unix-generated CSV files.'''
        delimiter = ','
        quotechar = '"'
        doublequote = True
        skipinitialspace = False
        lineterminator = '\n'
        quoting = QUOTE_ALL    # noqa

    register_dialect("unix", unix_dialect)    # noqa


#: Define 'unix dialect' as our base default.
DefaultDialect = unix_dialect


def parse(*data, **kwds):
    '''Parse `data` into a sheet.

    :param data: A collection of string lines to parse.

    :param dialect: The `csv.Dialect`:class: sub-class to be used in the
           reader.  Keyword only parameter.  If no value is given,
           `~csv.reader`:func: uses its default.

    :param mould: A function for moulding each cell value.  Keyword only
           parameter.

    :returns: The parsed matrix.

    Coercion:

    - When reading a value, Python version 2 doesn't accept unicode,
      so given data lines are coerced to be `str`:class: values.

    - Each cell is converted to unicode text; then processed with the
      `dialect` (if given and callable); and lastly, the `mould` function is
      used.

    '''
    from os import linesep
    from csv import reader
    from xoutil.eight import string_types, callable, string, text
    from xoutil.fp.tools import compose
    from xoutil.params import get_keyword_values
    mould, dialect = get_keyword_values(kwds, 'mould', 'dialect')
    cast = compose(*(f for f in (mould, dialect, text.force) if callable(f)))
    lines = (string.force(line + linesep) for line in data)
    rows = reader(lines, **({'dialect': dialect} if dialect else {}))
    return [[cast(cell) for cell in row] for row in rows]
