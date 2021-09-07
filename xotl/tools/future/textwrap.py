#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""Text wrapping and filling."""

import textwrap as _stdlib
from textwrap import *  # noqa
from textwrap import __all__  # noqa

__all__ = list(__all__)


def dedent(text, skip_firstline=False):
    r"""Remove any common leading whitespace from every line in text.

    This can be used to make triple-quoted strings line up with the left edge
    of the display, while still presenting them in the source code in indented
    form.

    Note that tabs and spaces are both treated as whitespace, but they are not
    equal: the lines ``"    hello"`` and ``"\thello"`` are considered to have
    no common leading whitespace.

    If `skip_firstline` is True, the first line is separated from the rest of
    the body.  This helps with docstrings that follow `257`:pep:.

    .. warning:: The `skip_firstline` argument is missing in standard library.

    """
    if skip_firstline:
        parts = text.split("\n", 1)
        if len(parts) > 1:
            subject, body = parts
        else:
            subject, body = parts[0], ""
        result = _stdlib.dedent(subject)
        if body:
            result += "\n" + _stdlib.dedent(body)
    else:
        result = _stdlib.dedent(text)
    return result
