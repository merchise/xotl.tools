#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""Enhanced data pretty printer."""

from pprint import *  # noqa
from pprint import __all__, pprint  # noqa

__all__ = list(__all__) + ["ppformat"]


def ppformat(obj):
    """Just like `pprint`:func: but always returning a result.

    :returns: The pretty formated text.
    :rtype: `unicode` in Python 2, `str` in Python 3.

    """
    import io

    stream = io.StringIO()
    pprint(obj, stream=stream)
    stream.seek(0)
    res = stream.read()
    if isinstance(res, str):
        return res
    else:
        from xotl.tools.future.codecs import safe_decode

        return safe_decode(res)
