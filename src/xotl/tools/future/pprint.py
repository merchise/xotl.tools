#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Enhanced data pretty printer."""

import io
from pprint import pprint

__all__ = ["ppformat"]


def ppformat(obj) -> str:
    """Just like `pprint`:func: but always returning a result.

    :returns: The pretty formated text.

    """
    stream = io.StringIO()
    pprint(obj, stream=stream)
    stream.seek(0)
    res = stream.read()
    return res
