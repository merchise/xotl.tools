#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Some additions for `string` standard module."""

from typing import Any, Optional, Pattern

# TODO: Functions starting with 'cut_' must be reviewed, maybe migrated to
# some module dedicated to "string trimming".
try:
    cut_prefix = str.removeprefix  # type: ignore
except AttributeError:

    def cut_prefix(self: str, prefix: str) -> str:
        """Removes the leading `prefix` if exists, else return `value`
        unchanged.

        In Python 3.9+ this is the same as `str.removeprefix`:func:.

        """
        from xotl.tools.future.codecs import safe_decode, safe_encode

        if isinstance(self, str) and isinstance(prefix, bytes):
            prefix = safe_decode(prefix)
        elif isinstance(self, bytes) and isinstance(prefix, str):
            prefix = safe_encode(prefix)
        return self[len(prefix) :] if self.startswith(prefix) else self


def cut_any_prefix(value: str, *prefixes: str) -> str:
    """Apply `cut_prefix`:func: for the first matching prefix."""
    result = prev = value
    i, top = 0, len(prefixes)
    while i < top and result == prev:
        prefix, i = prefixes[i], i + 1
        prev, result = result, cut_prefix(prev, prefix)
    return result


def cut_prefixes(value: str, *prefixes: str) -> str:
    """Apply `cut_prefix`:func: for all provided prefixes in order."""
    result = value
    for prefix in prefixes:
        result = cut_prefix(result, prefix)
    return result


try:
    cut_suffix = str.removesuffix  # type: ignore
except AttributeError:

    def cut_suffix(self: str, suffix: str) -> str:
        """Removes the tailing `suffix` if exists, else return `value`
        unchanged.

        In Python 3.9+ this is the same as `str.removesuffix`:func:.

        """
        from xotl.tools.future.codecs import safe_decode, safe_encode

        if isinstance(self, str) and isinstance(suffix, bytes):
            suffix = safe_decode(suffix)
        elif isinstance(self, bytes) and isinstance(suffix, str):
            suffix = safe_encode(suffix)
        # Since value.endswith('') is always true but value[:-0] is actually
        # always value[:0], which is always '', we have to explictly test for
        # len(suffix)
        if len(suffix) > 0 and self.endswith(suffix):
            return self[: -len(suffix)]
        else:
            return self


def cut_any_suffix(value: str, *suffixes: str) -> str:
    """Apply `cut_suffix`:func: for the first matching suffix."""
    result = prev = value
    i, top = 0, len(suffixes)
    while i < top and result == prev:
        suffix, i = suffixes[i], i + 1
        prev, result = result, cut_suffix(prev, suffix)
    return result


def cut_suffixes(value: str, *suffixes: str) -> str:
    """Apply `cut_suffix`:func: for all provided suffixes in order."""
    result = value
    for suffix in suffixes:
        result = cut_suffix(result, suffix)
    return result


def force_ascii(value: Any, encoding: Optional[str] = None) -> str:
    """Return the string normal form for the `value`

    Convert all non-ascii to valid characters using unicode 'NFKC'
    normalization.

    :param encoding: If `value` is not unicode, it is decoded before ASCII
           normalization using this encoding.  If not provided use the return
           of `~xotl.tools.future.codecs.force_encoding`:func:.

    .. versionchanged:: 1.8.7 Add parameter 'encoding'.

    .. versionchanged:: 2.1.0 Moved to `xotl.tools.string`:mod:.

    """
    import unicodedata

    from .future.codecs import safe_decode

    ASCII, IGNORE = "ascii", "ignore"
    if not isinstance(value, str):
        value = safe_decode(value, encoding=encoding)
    res = unicodedata.normalize("NFKD", value).encode(ASCII, IGNORE)
    return str(res, ASCII, IGNORE)


def slugify(
    value: Any,
    replacement="-",
    *,
    invalid_chars="",
    valid_chars="",
    encoding: str | None = None,
) -> str:
    """Return the normal-form of a given string value that is valid for slugs.

    Normalize `value` to ASCII using Unicode NFKD normalization and lowercase it.  The default valid
    characters are ``[_a-z0-9]``; replace runs of unwanted characters with `replacement` and strip
    them from the ends.

    Pass `replacement` as the first extra positional argument or as a keyword argument; it defaults
    to ``"-"``.  An empty string removes unwanted characters instead of separating them.  For
    compatibility, ``None`` and ``False`` also mean an empty replacement.  A non-string replacement
    raises `TypeError`, and a replacement containing characters explicitly marked invalid raises
    `ValueError`.

    The keyword `invalid_chars` removes characters from the valid set.  It defaults to an empty
    string; ``True`` means ``"_"``, and ``False`` or ``None`` means no additional invalid
    characters.
    The keyword `valid_chars` adds valid characters and accepts a string, an iterable of strings,
    or ``None``.  Both character options are keyword-only.

    The keyword `encoding` controls decoding of non-text values before `force_ascii`:func:
    normalization.

    Only `value` and `replacement` accept positional arguments.  Unknown keywords, extra positional
    arguments, and duplicate arguments raise `TypeError`.

    Examples:

      >>> slugify('  Á.e i  Ó  u  ') == 'a-e-i-o-u'
      True

      >>> slugify(' Á.e i  Ó  u  ', '.', invalid_chars='AU') == 'e.i.o'
      True

      >>> slugify('  Á.e i  Ó  u  ', valid_chars='.') == 'a.e-i-o-u'
      True

      >>> slugify('_x', '_') == '_x'
      True

      >>> slugify('-x', '_') == 'x'
      True

      >>> slugify(None) == 'none'
      True

      >>> slugify(1 == 1)  == 'true'
      True

      >>> slugify(1.0) == '1-0'
      True

      >>> slugify(135) == '135'
      True

      >>> slugify(123456, '', invalid_chars='52') == '1346'
      True

      >>> slugify('_x', '_') == '_x'
      True

    .. versionchanged:: 1.5.5 Added the `invalid_underscore` parameter.

    .. versionchanged:: 1.6.6 Replaced the `invalid_underscore` paremeter by
       `invalids`.  Added the `valids` parameter.

    .. versionchanged:: 1.7.2 Clarified the role of `invalids` with regards to
       `replacement`.

    .. versionchanged:: 1.8.0 Deprecate the `invalids` paremeter name in favor
       of `invalid_chars`, also deprecate the `valids` paremeter name in favor
       of `valid_chars`.

    .. versionchanged:: 1.8.7 Add parameter 'encoding'.

    .. versionchanged:: 2.1.0 Remove deprecated parameters `invalids` and
       `valids`.

    .. versionchanged:: 3.6.0
       Enforce the documented parameters through native Python argument binding, with character
       and encoding options keyword-only.  The legacy aliases `invalid` and `valid` are no
       longer accepted.

    """
    import re

    def _normalize(v):
        return force_ascii(v, encoding=encoding).lower()

    def _set(v):
        return re.escape("".join(set(_normalize(v))))

    if replacement in (None, False):
        # for backward compatibility
        replacement = ""
    elif isinstance(replacement, str):
        replacement = _normalize(replacement)
    else:
        raise TypeError(
            'slugify() replacement "{}" must be a string or None, not "{}".'.format(
                replacement, type(replacement)
            )
        )
    if invalid_chars is True:
        # Backward compatibility with former `invalid_underscore` argument
        invalid_chars = "_"
    elif invalid_chars in {None, False}:
        invalid_chars = ""
    else:
        if not isinstance(invalid_chars, str):
            invalid_chars = "".join(invalid_chars)
        invalid_chars = _set(invalid_chars)
    invalid_regex: Optional[Pattern]
    if invalid_chars:
        invalid_regex = re.compile(r"[{}]+".format(invalid_chars))
        if invalid_regex.search(replacement):
            raise ValueError(
                'slugify() replacement "{}" must not contain any invalid character.'.format(
                    replacement
                )
            )
    else:
        invalid_regex = None
    if valid_chars is None:
        valid_chars = ""
    else:
        if not isinstance(valid_chars, str):
            valid_chars = "".join(valid_chars)
        valid_chars = _set(valid_chars)
        valid_chars = _set(re.sub(r"[0-9a-z]+", "", valid_chars))
    valid_chars = re.compile(r"[^_0-9a-z{}]+".format(valid_chars))
    # calculate result
    repl = "\t" if replacement else ""
    res = valid_chars.sub(repl, _normalize(value))
    if invalid_regex:
        res = invalid_regex.sub(repl, res)
    if repl:
        # convert two or more replacements in only one instance
        r = r"{}".format(re.escape(repl))
        res = re.sub(r"({r}){{2,}}".format(r=r), repl, res)
        # remove start and end more replacement instances
        res = re.sub(r"(^{r}+|{r}+$)".format(r=r), "", res)
        res = re.sub(r"[\t]", replacement, res)
    return res


def error2str(error):
    """Convert an error to string."""
    if isinstance(error, str):
        return error
    elif isinstance(error, BaseException):
        tname = type(error).__name__
        res = str(error)
        if tname in res:
            return res
        else:
            return ": ".join((tname, res)) if res else tname
    elif isinstance(error, type) and issubclass(error, BaseException):
        return error.__name__
    else:
        prefix = str("unknown error: ")
        cls = error if isinstance(error, type) else type(error)  # force type
        tname = cls.__name__
        if cls is error:
            res = tname
        else:
            res = str(error)
            if tname not in res:
                res = str("{}({})").format(tname, res) if res else tname
        return prefix + res


def make_a10z(string: str) -> str:
    """Utility to find out that "internationalization" is "i18n".

    Examples::

       >>> print(make_a10z('parametrization'))
       p13n
    """
    return string[0] + str(len(string[1:-1])) + string[-1]
