#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Some additions for `string` standard module.

In Python 3 `str` is always unicode but `unicode` and `basestring` types
doesn't exists.  `bytes` type can be used as an array of one byte each item.

"""
from typing import Any, Optional, Pattern

from xotl.tools.deprecation import deprecated  # noqa
from xotl.tools.deprecation import import_deprecated  # noqa


_MIGRATED_TO_CODECS = ("force_encoding", "safe_decode", "safe_encode")

import_deprecated("xotl.tools.future.codecs", *_MIGRATED_TO_CODECS)


@deprecated
def safe_strip(value):
    """Removes the leading and tailing space-chars from `value` if string, else
    return `value` unchanged.

    """
    return value.strip() if isinstance(value, str) else value


# TODO: Functions starting with 'cut_' must be reviewed, maybe migrated to
# some module dedicated to "string trimming".
try:
    cut_prefix = str.removeprefix
except AttributeError:

    def cut_prefix(self: str, prefix: str) -> str:
        """Removes the leading `prefix` if exists, else return `value`
        unchanged.

        In Python 3.9+ this is the same as `str.removeprefix`:func:.

        """
        from xotl.tools.future.codecs import safe_encode, safe_decode

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
    cut_suffix = str.removesuffix
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


def force_ascii(value: Any, encoding: str = None) -> str:
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


def slugify(value: Any, *args, **kwds) -> str:
    """Return the normal-form of a given string value that is valid for slugs.

    Convert all non-ascii to valid characters, whenever possible, using
    unicode 'NFKC' normalization and lower-case the result.  Replace unwanted
    characters by the value of `replacement` (remove extra when repeated).

    Default valid characters are ``[_a-z0-9]``.  Extra arguments
    `invalid_chars` and `valid_chars` can modify this standard behaviour, see
    next:

    :param value: The source value to slugify.

    :param replacement: A character to be used as replacement for unwanted
           characters.  Could be both, the first extra positional argument, or
           as a keyword argument.  Default value is a hyphen ('-').

           There will be a contradiction if this argument contains any invalid
           character (see `invalid_chars`).  ``None``, or ``False``, will be
           converted converted to an empty string for backward compatibility
           with old versions of this function, but not use this, will be
           deprecated.

    :param invalid_chars: Characters to be considered invalid.  There is a
           default set of valid characters which are kept in the resulting
           slug.  Characters given in this parameter are removed from the
           resulting valid character set (see `valid_chars`).

           Extra argument values can be used for compatibility with
           `invalid_underscore` argument in deprecated `normalize_slug`
           function:

           - ``True`` is a synonymous of underscore ``"_"``.

           - ``False`` or ``None``: An empty set.

           Could be given as a name argument or in the second extra positional
           argument.  Default value is an empty set.

    :param valid_chars: A collection of extra valid characters.  Could be
           either a valid string, any iterator of strings, or ``None`` to use
           only default valid characters.  Non-ASCII characters are ignored.

    :param encoding: If `value` is not a text (unicode), it is decoded before
           `ASCII normalization <force_ascii>`:func:.

    Examples::

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

    """
    import re

    from .params import ParamManager
    from .values import compose, istype
    from .values.simple import not_false, ascii_coerce

    _str = compose(not_false(""), istype(str))
    _ascii = compose(_str, ascii_coerce)

    # local functions
    def _normalize(v):
        return force_ascii(v, encoding=encoding).lower()

    def _set(v):
        return re.escape("".join(set(_normalize(v))))

    getarg = ParamManager(args, kwds)
    replacement = getarg("replacement", 0, default="-", coercers=(str,))
    invalid_chars = getarg("invalid_chars", "invalid", 0, default="", coercers=_ascii)
    valid_chars = getarg("valid_chars", "valid", 0, default="", coercers=_ascii)
    encoding = getarg("encoding", default=None)
    replacement = args[0] if args else kwds.pop("replacement", "-")
    # TODO: check unnecessary arguments, raising errors
    if replacement in (None, False):
        # for backward compatibility
        replacement = ""
    elif isinstance(replacement, str):
        replacement = _normalize(replacement)
    else:
        raise TypeError(
            'slugify() replacement "{}" must be a string or None,'
            ' not "{}".'.format(replacement, type(replacement))
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
                'slugify() replacement "{}" must not contain '
                "any invalid character.".format(replacement)
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


@deprecated(slugify)
def normalize_slug(value: Any, *args, **kwds) -> str:
    return slugify(value, *args, **kwds)


del deprecated, import_deprecated
