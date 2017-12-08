#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Extensions to standard library `mimetype`:mod:.

This module reexport all functions the *current* version of Python.

.. versionadded:: 1.8.4

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import mimetypes as _stdlib
from mimetypes import *  # noqa

from xoutil.symbols import Unset


def guess_type(url, strict=True, default=(None, None)):
    '''Guess the type of a file based on its filename or URL, given by url.

    This is the same as `mimetypes.guess_type`:func: with the addition of the
    `default` keyword

    '''
    type, encoding = _stdlib.guess_type(url, strict=strict)
    if default is not Unset and type is None:
        type, encoding = default
    return type, encoding
