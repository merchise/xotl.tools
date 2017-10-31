#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.future.pprint
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-05-06
# Migrated to 'future' on 2016-09-20

'''Enhanced data pretty printer.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

from pprint import *    # noqa

from pprint import __all__    # noqa
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
