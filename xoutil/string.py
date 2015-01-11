#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.string
# ---------------------------------------------------------------------
# Copyright (c) 2012-2015 Merchise Autrement and Contributors
# All rights reserved.
#
# Author: Medardo Rodríguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Feb 17, 2012

'''Exposes all original `string` module functionalities, with some general
additions.

In this module `str` and `unicode` types are not used because Python 2.x and
Python 3.x treats strings differently, `bytes` and `_unicode` will be used
instead with the following conventions:

- In Python 2.x `str` is synonym of `bytes` and both (`unicode` and 'str') are
  both string types inheriting form `basestring`.  `_unicode` is synonym of
  `unicode`.

- In Python 3.x `str` is always unicode but `unicode` and `basestring` types
  doesn't exists. `bytes` type can be used as an array of one byte each item.

  `_unicode` is synonym of `str`.

  Many methods are readjusted to these conditions.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from xoutil.deprecation import deprecated as _deprecated
from six import (string_types as _str_base,
                 text_type as _unicode,
                 binary_type as _bytes,
                 PY3 as _py3k)

from xoutil.modules import copy_members as _copy_python_module_members
_pm = _copy_python_module_members()

Formatter = _pm.Formatter     # Redundant but needed to avoid IDE errors

del _copy_python_module_members, _pm


def force_encoding(encoding=None):
    '''Validates an encoding value; if None use `locale.getlocale()[1]`; else
    return the same value.

    .. versionadded:: 1.2.0

    '''
    # TODO: Maybe use only `sys.getdefaultencoding()`
    import locale
    return encoding or locale.getpreferredencoding() or 'UTF-8'


def safe_decode(s, encoding=None):
    '''Similar to bytes `decode` method returning unicode.

    Decodes `s` using the given `encoding`, or determining one from the system.

    Returning type depend on python version; if 2.x is `unicode` if 3.x `str`.

    .. versionadded:: 1.1.3

    '''
    if isinstance(s, _unicode):
        return s
    else:
        encoding = force_encoding(encoding)
        try:
            # In Python 3 str(b'm') returns the string "b'm'" and not just "m",
            # this fixes this.
            return _unicode(s, encoding, 'replace')
        except:
            # For numbers and other stuff.
            return _unicode(s)


def safe_encode(u, encoding=None):
    '''Similar to unicode `encode` method returning bytes.

    Encodes `u` using the given `encoding`, or determining one from the system.

    Returning type is always `bytes`; but in python 2.x is also `str`.

    .. versionadded:: 1.1.3

    '''
    if isinstance(u, bytes):
        return u
    else:
        encoding = force_encoding(encoding)
        try:
            if isinstance(u, _str_base):
                # In Python 2.x bytes does not allows an encoding argument.
                return bytes(u)
            else:
                return _unicode(u).encode(encoding, 'replace')
        except:
            return _unicode(u).encode(encoding, 'replace')


def safe_join(separator, iterable, encoding=None):
    '''Similar to `join` method in string objects `separator.join(iterable)`, a
    string which is the concatenation of the strings in the `iterable` with
    `separator` as intermediate between elements. Return unicode or bytes
    depending on type of `separator` and each item in `iterable`.

    `encoding` is used in case of error to concatenate bytes + unicode.

    This function must be deprecated in Python 3.

    .. versionadded:: 1.1.3

    .. warning:: The `force_separator_type` was removed in version 1.2.0.

    '''
    try:
        return separator.join(iterable)
    except:
        pass
    encoding = force_encoding(encoding)
    empty = True
    for item in iterable:
        if empty:
            res = item
            empty = False
        else:
            for tail in (separator, item):
                try:
                    res += tail
                except:
                    res = (safe_decode(res, encoding) +
                           safe_decode(item, encoding))
    return res if not empty else type(separator)()


# Makes explicit the deprecation warning for py3k.
if _py3k:
    safe_join = _deprecated('builtin join method of str',
                            'safe_join is deprecated for Python 3. Use '
                            'builtin join method of str.')(safe_join)


def safe_strip(value):
    '''Removes the leading and tailing space-chars from `value` if string, else
    return `value` unchanged.

    .. versionadded:: 1.1.3

    '''
    return value.strip() if isinstance(value, (_unicode, _bytes)) else value


def cut_prefix(value, prefix):
    '''Removes the leading `prefix` if exists, else return `value`
    unchanged.

    '''
    from six import text_type as str, binary_type as bytes
    if isinstance(value, str) and isinstance(prefix, bytes):
        prefix = safe_decode(prefix)
    elif isinstance(value, bytes) and isinstance(prefix, str):
        prefix = safe_encode(prefix)
    return value[len(prefix):] if value.startswith(prefix) else value


def cut_any_prefix(value, *prefixes):
    '''Apply `cut_prefix`:func: for the first matching prefix.'''
    result = prev = value
    i, top = 0, len(prefixes)
    while i < top and result == prev:
        prefix, i = prefixes[i], i + 1
        prev, result = result, cut_prefix(prev, prefix)
    return result


def cut_prefixes(value, *prefixes):
    '''Apply `cut_prefix`:func: for all provided prefixes in order.'''
    result = value
    for prefix in prefixes:
        result = cut_prefix(result, prefix)
    return result


def cut_suffix(value, suffix):
    '''Removes the tailing `suffix` if exists, else return `value`
    unchanged.

    '''
    from six import text_type as str, binary_type as bytes
    if isinstance(value, str) and isinstance(suffix, bytes):
        suffix = safe_decode(suffix)
    elif isinstance(value, bytes) and isinstance(suffix, str):
        suffix = safe_encode(suffix)
    return value[:-len(suffix)] if value.endswith(suffix) else value


def cut_any_suffix(value, *suffixes):
    '''Apply `cut_suffix`:func: for the first matching suffix.'''
    result = prev = value
    i, top = 0, len(suffixes)
    while i < top and result == prev:
        suffix, i = suffixes[i], i + 1
        prev, result = result, cut_suffix(prev, suffix)
    return result


def cut_suffixes(value, *suffixes):
    '''Apply `cut_suffix`:func: for all provided suffixes in order.'''
    result = value
    for suffix in suffixes:
        result = cut_suffix(result, suffix)
    return result


def capitalize_word(value):
    'Capitalizes the first char of value'
    if value and value[0].islower():
        return value[0].upper() + value[1:]
    else:
        return value


def capitalize(value, title=True):
    '''Capitalizes value according to whether it should be title-like.

    Title-like means it will capitalize every word but the 3-letters or less
    unless its the first word::

        >>> capitalize('a group is its own worst enemy')
        'A Group is its own Worst Enemy'

    (This may be odd because, in the example above, own should be capitalized.)

    Return bytes or unicode depending on type of `value`.

        >>> type(capitalize(_unicode('something'))) is _unicode
        True

        >>> type(capitalize(str('something'))) is str
        True

    '''
    space, empty = (' ', '') if isinstance(value, _unicode) else (b' ', b'')
    words = value.split() if value else None
    if words:
        count = len(words) if title else 1
        for i in range(count):
            word = words[i]
            if len(word) > 3 or i == 0:
                word = capitalize_word(word)
                words[i] = word
        return space.join(words)
    else:
        return empty


# TODO: Document and fix all these "normalize_..." functions
def normalize_unicode(value):
    # FIXME: i18n
    if (value is None) or (value is str('')):
        return ''
    elif value is True:
        return 'Sí'
    elif value is False:
        return 'No'
    else:
        return safe_decode(value)


def normalize_name(value):
    return capitalize(normalize_unicode(value))


def normalize_title(value):
    return capitalize(normalize_unicode(value), True)


def normalize_str(value):
    import re
    is_bytes = isinstance(value, bytes)
    regex, sep = r'(\S+)\s*', ' '
    if is_bytes:
        regex, sep = bytes(regex), bytes(sep)
    regex = re.compile(regex)
    matches = regex.findall(value)
    names = (m.capitalize() if len(m) >= 3 else m.lower() for m in matches)
    return sep.join(names)


def normalize_ascii(value):
    '''Return the string normal form for the :param:`value`

    Convert all non-ascii to valid characters using unicode 'NFKC'
    normalization.
    '''
    import unicodedata
    if not isinstance(value, _unicode):
        value = safe_decode(value)
    res = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    return safe_decode(res)


def normalize_slug(value, replacement='-', invalids=None, valids=None):
    '''Return the string normal form, valid for slugs, for the :param:`value`

    Convert all non-ascii to valid characters using unicode 'NFKC'
    normalization.

    Lower-case the result.

    Replace unwanted characters by :param:`replacement`, repetition of given
    pattern will be converted to only one instance.

    ``[_a-z0-9]`` are assumed as valid characters.  Extra arguments can modify
    this standard behaviour:

    :param invalids: Any collection of characters added to these that are
           normally invalids (non-ascii or not included in valid characters).
           Boolean ``True`` can be passed as a synonymous of ``"_"`` for
           compatibility with old ``invalid_underscore`` argument.  ``False``
           or ``None`` are assumed as an empty set for invalid characters.

    :param valids: A collection of extra valid characters (all non-ascii
           characters are ignored).  This parameter could be either a valid
           string, any iterator of valid strings of characters, or ``None`` to
           use only default valid characters (See above).

    Parameters :param:`value` and :param:`replacement` could be of any
    (non-string) type, these values are normalized and converted to lower-case
    ASCII strings.

    Examples::

      >>> normalize_slug('  Á.e i  Ó  u  ') == 'a-e-i-o-u'
      True

      >>> normalize_slug('  Á.e i  Ó  u  ', '.', invalids='AU') == 'e.i.o'
      True

      >>> normalize_slug('  Á.e i  Ó  u  ', valids='.') == 'a.e-i-o-u'
      True

      >>> normalize_slug(None) == 'none'
      True

      >>> normalize_slug(1 == 1)  == 'true'
      True

      >>> normalize_slug(1.0) == '1-0'
      True

      >>> normalize_slug(135) == '135'
      True

      >>> normalize_slug(123456, '', invalids='52') == '1346'
      True

    .. versionchanged:: 1.5.5 Added the `invalid_underscore` parameter.

    .. versionchanged:: 1.6.6 Replaced the `invalid_underscore` paremeter by
       `invalids`.  Added the `valids` parameter.

    '''
    import re
    # local functions
    _normalize = lambda v: normalize_ascii(v).lower()
    _set = lambda v: ''.join(set(v))
    _esc = lambda v: re.escape(_set(v))
    _from_iter = lambda v: ''.join(i for i in v)
    # check and adjust arguments
    if replacement in (None, False):
        replacement = ''
    elif isinstance(replacement, _str_base):
        replacement = normalize_ascii(replacement)    # TODO: or _normalize?
    else:
        msg = '`replacement` (%s) must be a string or None, not `%s`.'
        raise TypeError(msg % (replacement, type(replacement)))
    if invalids is True:
        # Backward compatibility with former `invalid_underscore` argument
        invalids = '_'
    elif invalids in {None, False}:
        invalids = ''
    else:
        if not isinstance(invalids, _str_base):
            invalids = _from_iter(invalids)
        invalids = _esc(_normalize(invalids))
    if valids is None:
        valids = ''
    else:
        if not isinstance(valids, _str_base):
            valids = _from_iter(valids)
        valids = _esc(re.sub(r'[0-9a-b]+', '', _normalize(valids)))
    # calculate result
    res = _normalize(value)
    regex = re.compile(r'[^_a-z0-9%s]+' % valids)
    res = regex.sub(replacement, res)
    if invalids:
        regex = re.compile(r'[%s]+' % invalids)
        res = regex.sub(replacement, res)
    if replacement:
        r = {'r': r'%s' % re.escape(replacement)}
        regex = re.compile(r'(%(r)s){2,}' % r)
        res = regex.sub(replacement, res)
        regex = re.compile(r'(^%(r)s+|%(r)s+$)' % r)
        res = regex.sub('', res)
    return res


def strfnumber(number, format_spec='%0.2f'):
    res = format_spec % number
    if '.' in res:
        res = res.rstrip('0')
        if res.endswith('.'):
            res = res[:-1]
    return res


def parse_boolean(value):
    '''Parse a boolean from any value given a special treatment to
    strings.

    >>> parse_boolean('trUe')
    True

    >>> parse_boolean('faLSe')
    False

    '''
    if isinstance(value, _str_base):
        value = value.strip()
        if value:
            if value.isdigit():
                return bool(int(value))
            else:
                if isinstance(value, bytes):
                    falses = (b'false', b'no', b'not')
                else:
                    falses = ('false', 'no', 'not')
                return value.lower() not in falses
        else:
            return False
    else:
        return bool(value)


def parse_url_int(value, default=None):
    '''Parse an integer URL argument. Some operations treat simple
    arguments as a list of one element.

    '''
    if isinstance(value, (list, tuple, set)) and len(value) > 0:
        value = value[0]
    try:
        return int(safe_strip(value))
    except:
        return default


def force_str(value, encoding=None):
    '''Force to string, the type is different in Python 2 or 3 (bytes or
    unicode).

    :param value: The value to convert to `str`.
    :param encoding: The encoding which should be used if either encoding
                     or decoding should be performed on `value`.

                     The default is to use the same default as
                     :func:`safe_encode` or :func:`safe_decode`.

    .. versionadded:: 1.2.0

    '''
    if isinstance(value, str):
        return value
    elif str is bytes:      # Python 2
        return safe_encode(value, encoding)
    else:
        return safe_decode(value, encoding)


def make_a10z(string):
    '''Utility to find out that "internationalization" is "i18n".

    Examples::

       >>> print(make_a10z('parametrization'))
       p13n
    '''
    return string[0] + str(len(string[1:-1])) + string[-1]


from six.moves import input

input = _deprecated(
    input,
    "xoutil.string.input is deprecated.  Use six.moves.input"
)(input)
