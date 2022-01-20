#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""Utils for Web applications."""

__all__ = ["slugify"]


# TODO: Why not deprecate this and use standard `xotl.tools.string.slugify`.
def slugify(s, entities=True, decimal=True, hexadecimal=True):  # pragma: no cover  # noqa
    """Convert a string to a slug representation.

    Normalizes string, converts to lower-case, removes non-alpha characters,
    and converts spaces to hyphens.

    Parts from http://www.djangosnippets.org/snippets/369/

        >>> slugify("Manuel Vázquez Acosta")    # doctest: +SKIP
        'manuel-vazquez-acosta'

    If `s` and `entities` is True (the default) all HTML entities
    are replaced by its equivalent character before normalization::

        >>> slugify("Manuel V&aacute;zquez Acosta")   # doctest: +SKIP
        'manuel-vazquez-acosta'

    If `entities` is False, then no HTML-entities substitution is made::

        >>> value = "Manuel V&aacute;zquez Acosta"
        >>> slugify(value, entities=False)  # doctest: +SKIP
        'manuel-v-aacute-zquez-acosta'

    If `decimal` is True, then all entities of the form ``&#nnnn`` where
    `nnnn` is a decimal number deemed as a unicode codepoint, are replaced by
    the corresponding unicode character::

        >>> slugify('Manuel V&#225;zquez Acosta')  # doctest: +SKIP
        'manuel-vazquez-acosta'

        >>> value = 'Manuel V&#225;zquez Acosta'
        >>> slugify(value, decimal=False)  # doctest: +SKIP
        'manuel-v-225-zquez-acosta'


    If `hexadecimal` is True, then all entities of the form ``&#nnnn`` where
    `nnnn` is a hexdecimal number deemed as a unicode codepoint, are replaced
    by the corresponding unicode character::

        >>> slugify('Manuel V&#x00e1;zquez Acosta')  # doctest: +SKIP
        'manuel-vazquez-acosta'

        >>> slugify('Manuel V&#x00e1;zquez Acosta', hexadecimal=False)  # doctest: +SKIP  # noqa
        'manuel-v-x00e1-zquez-acosta'

    .. deprecated:: 2.1.0 Use `xotl.tools.strings.slugify`:func:.

    """
    import re

    from xotl.tools.future.codecs import safe_decode
    from xotl.tools.string import slugify

    if not isinstance(s, str):
        s = safe_decode(s)
    if entities:
        try:
            from htmlentitydefs import name2codepoint
        except ImportError:
            # Py3k: The ``htmlentitydefs`` module has been renamed to
            # ``html.entities`` in Python 3
            from html.entities import name2codepoint
        s = re.sub(
            str("&(%s);") % str("|").join(name2codepoint),
            lambda m: chr(name2codepoint[m.group(1)]),
            s,
        )
    if decimal:
        try:
            s = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), s)
        except Exception:  # TODO: @med which exceptions are expected?
            pass
    if hexadecimal:
        try:
            s = re.sub(r"&#x([\da-fA-F]+);", lambda m: chr(int(m.group(1), 16)), s)
        except Exception:  # TODO: @med which exceptions are expected?
            pass
    return slugify(s, "-")
