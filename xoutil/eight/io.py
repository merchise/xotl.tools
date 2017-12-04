#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Extensions to Python's ``io`` module.

You may use it as drop-in replacement of ``io``.  Although we don't document
all items here.  Refer to `io`:mod: documentation.

In Python 2, buil-int `open`:func: is different from `io.open`:func:; in
Python 3 are the same function.

So, generated files with the built-in funtion in Python 2, can not be
processed using *abc* types, for example::

  f = open('test.rst')
  assert isinstance(f, io.IOBase)

will fail in Python 2 and not in Python 3.

Another incompatibilities:

- `file` type doesn't exists in Python 3.

- Python 2 instances created with `io.StringIO`:class`, or with
  `io.open`:func: using text mode, don't accept `str` values, so it will be
  better to use any of the standards classes (`StringIO.StringIO`:class:,
  `cStringIO.StringIO`:class: or `open`:func: built-in).

.. versionadded:: 1.7.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

# TODO: This is the initial state for a in-progress module.

from io import *    # noqa
from io import IOBase

# Next three members are not included in ``__all__`` definition

from io import (DEFAULT_BUFFER_SIZE, IncrementalNewlineDecoder,    # noqa
                OpenWrapper)


def is_file_like(obj):
    '''Return if `obj` is a valid file type or not.'''
    from xoutil.eight import python_version, callable
    types = (file, IOBase) if python_version == 2 else (IOBase, )
    if isinstance(obj, types):
        return True
    else:
        methods = ('close', 'write', 'read')
        return all(callable(getattr(obj, name, None)) for name in methods)
