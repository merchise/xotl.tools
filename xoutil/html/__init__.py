#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.html
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-04-18

'''This module defines utilities to manipulate HTML.

This module backports several utilities from Python 3.2.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from xoutil.eight import _py3, iteritems as iteritems_
from xoutil.string import safe_decode

import warnings
warnings.warn('xoutil.html is deprecated')


if _py3:
    from html import entities
    from html import parser
else:
    import htmlentitydefs as entities
    import HTMLParser as parser


entities.entitydefs_unicode = {}
entities.entitydefs_utf8 = {}

for name, entity in iteritems_(entities.entitydefs):
    text = entities.entitydefs_unicode[name] = safe_decode(entity, 'latin-1')
    entities.entitydefs_utf8[name] = text.encode('utf-8')
del name, entity, safe_decode, iteritems_


def _further_escape(s):
    import re
    from xoutil.string import safe_encode
    ASCII = getattr(re, 'ASCII', 0)  # Py3k
    what = re.compile(br'[\x00-\x1F\x80-\xFF]', ASCII)
    res, pos = b'', 0
    for match in what.finditer(s):
        char, start, end = match.group(), match.start(), match.end()
        assert start + 1 == end
        res += s[pos:start]
        res += b'&#' + safe_encode(str(ord(char))) + b';'
        pos = end
    res += s[pos:]
    return res

import sys
_py32 = sys.version_info >= (3, 2)
del sys

if not _py32:
    # The following is a modified copy from the Python 3.2 standard library, to
    # make xoutil forwards compatible. The modification is needed to cope with
    # the bytes/unicode issues in Python 2.7
    _escape_map = {ord('&'): '&amp;', ord('<'): '&lt;', ord('>'): '&gt;'}
    _escape_map_full = {ord('&'): '&amp;', ord('<'): '&lt;', ord('>'): '&gt;',
                        ord('"'): '&quot;', ord('\''): '&#x27;'}

    # NB: this is a candidate for a bytes/string polymorphic interface

    def escape(s, quote=True):
        """Replace special characters "&", "<" and ">" to HTML-safe sequences

        If the optional flag quote is true (the default), the quotation mark
        characters, both double quote (") and single quote (') characters are
        also translated.

        """
        from xoutil.eight import text_type
        from xoutil.string import safe_decode, safe_encode
        if not isinstance(s, text_type):
            arg = safe_decode(s)
        else:
            arg = s
        if quote:
            res = arg.translate(_escape_map_full)
        else:
            res = arg.translate(_escape_map)
        if not isinstance(res, type(s)):
            return safe_encode(res)
        return res

else:
    from html import escape    # noqa


del _py3, _py32


__all__ = (str('entities'), str('parser'), str('escape'))
