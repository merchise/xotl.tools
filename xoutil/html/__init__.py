#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''This module defines utilities to manipulate HTML.

This module backports several utilities from Python 3.2.

Because now we deprecated it, we moved here documentation to remove it in one
shot.


`xoutil.html.entities` -- Definitions of HTML general entities
==============================================================

This module defines tree dictionaries, ``name2codepoint``, ``codepoint2name``,
and ``entitydefs``.

``entitydefs`` is used to provide the `entitydefs` attribute of the
``xoutil.html.parser.HTMLParser`` class.  The definition provided here contains
all the entities defined by XHTML 1.0 that can be handled using simple textual
substitution in the Latin-1 character set (ISO-8859-1).

.. data:: entitydefs

   A dictionary mapping XHTML 1.0 entity definitions to their replacement text
   in ISO Latin-1.

.. data:: name2codepoint

   A dictionary that maps HTML entity names to the Unicode codepoints.

.. data:: codepoint2name

   A dictionary that maps Unicode codepoints to HTML entity names


`xoutil.html.parser` -- A simple parser that can handle HTML and XHTML
======================================================================

This module defines a class HTMLParser which serves as the basis for parsing
text files formatted in HTML (HyperText Mark-up Language) and XHTML.

.. warning:: This module has not being made Python 2.7 and 3.2 compatible.

.. class:: HTMLParser(strict=True)

   Create a parser instance. If strict is True (the default), invalid HTML
   results in `HTMLParseError`:class: exceptions [1]. If strict is False, the
   parser uses heuristics to make a best guess at the intention of any invalid
   HTML it encounters, similar to the way most browsers do. Using strict=False
   is advised.

   An :class`HTMLParser` instance is fed HTML data and calls handler methods
   when start tags, end tags, text, comments, and other markup elements are
   encountered. The user should subclass HTMLParser and override its methods to
   implement the desired behavior.

   This parser does not check that end tags match start tags or call the
   end-tag handler for elements which are closed implicitly by closing an outer
   element.

   .. versionchanged:: 3.2 strict keyword added

.. class:: HTMLParseError

   Exception raised by the `HTMLParser`:class: class when it encounters an
   error while parsing and strict is True. This exception provides three
   attributes: msg is a brief message explaining the error, lineno is the
   number of the line on which the broken construct was detected, and offset is
   the number of characters into the line at which the construct starts.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

from xoutil.eight import python_version, iteritems as iteritems_
from xoutil.future.codecs import safe_decode

import warnings
warnings.warn('xoutil.html is deprecated')
del warnings


if python_version == 3:
    from html import entities
    from html import parser
else:
    import htmlentitydefs as entities
    import HTMLParser as parser  # noqa


entities.entitydefs_unicode = {}
entities.entitydefs_utf8 = {}

for name, entity in iteritems_(entities.entitydefs):
    text = entities.entitydefs_unicode[name] = safe_decode(entity, 'latin-1')
    entities.entitydefs_utf8[name] = text.encode('utf-8')
del name, entity, safe_decode, iteritems_


def _further_escape(s):
    import re
    from xoutil.future.codecs import safe_encode
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


if python_version < 3.2:
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
        from xoutil.future.codecs import safe_decode, safe_encode
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


__all__ = (str('entities'), str('parser'), str('escape'))
