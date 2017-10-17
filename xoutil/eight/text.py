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


def decode(buffer, encoding=None):
    ''''Decode any buffer using the codec registered for encoding.'''
    from xoutil.future.codecs import safe_decode
    return safe_decode(buffer, encoding=encoding)
