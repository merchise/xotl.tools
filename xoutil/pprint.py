#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.pprint
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-05-06

'''Enhanced data pretty printer.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from xoutil.modules import copy_members as _copy_members
import pprint as _pm
_copy_members(_pm)

pprint = _pm.pprint  # Avoid IDE complaints

from xoutil.names import strlist as strs
__all__ = strs('ppformat', *getattr(_pm, '__all__', dir(_pm)))
del strs
del _pm, _copy_members


def ppformat(obj):
    '''Just like :func:`pprint` but always returns the result instead of
    writing it to a stream.

    :returns: The pretty formated text.
    :rtype: `unicode` in Python 2, `str` in Python 3.

    '''
    import io
    from xoutil.eight import _py3, text_type
    if _py3:
        stream = io.StringIO()
    else:
        stream = io.BytesIO()
    pprint(obj, stream=stream)
    stream.seek(0)
    res = stream.read()
    if isinstance(res, text_type):
        return res
    else:
        from xoutil.string import safe_decode
        return safe_decode(res)
