#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Enhanced data pretty printer.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

from pprint import *    # noqa
from pprint import __all__, pprint    # noqa
__all__ = list(__all__) + ['ppformat']

from xoutil.deprecation import deprecate_linked
deprecate_linked()
del deprecate_linked


def ppformat(obj):
    '''Just like `pprint`:func: but always returning a result.

    :returns: The pretty formated text.
    :rtype: `unicode` in Python 2, `str` in Python 3.

    '''
    import io
    from xoutil.eight import python_version, text_type
    if python_version == 3:
        stream = io.StringIO()
    else:
        stream = io.BytesIO()
    pprint(obj, stream=stream)
    stream.seek(0)
    res = stream.read()
    if isinstance(res, text_type):
        return res
    else:
        from xoutil.future.codecs import safe_decode
        return safe_decode(res)
