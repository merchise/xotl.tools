#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""CSV parsing and writing extensions.

This module is an extension of `csv`:mod: Python standard module, it provides
classes and tools that assist in the reading and writing of `Comma Separated
Value (CSV)`:abbr: files, and implements the interface described by PEP
`305`:pep:.

"""


from csv import *  # noqa
from csv import unix_dialect
import csv as _stdlib  # noqa


#: Define 'unix dialect' as our base default for inheritance.
DefaultDialect = unix_dialect

reader = _stdlib.reader


def parse(data, *dialect, **options):
    r"""Parse `data` into a sheet.

    This function has the exact parameters protocol as `~csv.reader`:func:\ ::

      parse(data [, dialect='excel'] [, optional keyword options])

    :param data: Can be any object that returns a line of input for each
           iteration, such as a file object or a list.

    :param dialect: An optional parameter can be given which is used to define
           a set of parameters specific to a particular CSV dialect.  It may
           be an instance of a subclass of the `~csv.Dialect`:class: class or
           one of the strings returned by the `~csv.list_dialects`:func:
           function.

    The other optional keyword arguments can be given to override
    individual formatting parameters in the current `dialect`.

    When reading a value, `csv`:mod: for Python version 2 doesn't accept
    unicode text, so given data lines are forced to be `str`:class: values
    before processed by `~csv.reader`:func:.  Each cell is converted to
    unicode text after read.

    :returns: The parsed matrix.

    A short usage example::

      >>> from xotl.tools.future import csv
      >>> with open('test.csv', newline='') as data:
      ...     matrix = csv.parse(data)
      ...     for row in matrix:
      ...         print(', '.join(row))
      Last name, First Name
      van Rossum, Guido
      Stallman, Richard

    """
    string_force = text_force = str  # They were different in Python 2.
    rows = reader((string_force(line) for line in data), *dialect, **options)
    return [[text_force(cell) for cell in row] for row in rows]
