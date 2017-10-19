#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Text handling, strings can be part of internationalization processes.

See `py-string-ambiguity`:any: for more information.


.. versionadded:: 1.8.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)


def force(buffer, encoding=None):
    '''Convert any value to standard `text` type in a safe way.

    The standard text type is ``unicode`` in Python 2 and ``str`` in
    Python 3.

    '''
    from xoutil.future.codecs import safe_decode
    return safe_decode(buffer, encoding=encoding)


def safe_join(separator, iterable, encoding=None):
    '''Similar to `join` method in string objects.

    The semantics is equivalent to ``separator.join(iterable)`` but forcing
    separator and items to be the valid instances of standard `text` type
    (``unicode`` in Python 2 and ``str`` in Python 3).

    For example::

      >>> safe_join('-', range(6))
      '0-1-2-3-4-5'

    Check that the expression ``'-'.join(range(6))`` raises a ``TypeError``.

    :param encoding: used to allow control, but won't be common to use it.

    '''
    sep = force(separator, encoding)
    return sep.join(force(item, encoding) for item in iterable)
