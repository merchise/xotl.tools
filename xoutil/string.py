#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.string
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# Copyright (c) 2012 Medardo Rodriguez
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
Python 3.x treats strings differently.  `bytes` and `text_type` will be used
instead with the following conventions:

- In Python 2.x `str` is synonym of `bytes` and both (`unicode` and 'str') are
  both string types inheriting form `basestring`.

- In Python 3.x `str` is always unicode but `unicode` and `basestring` types
  doesn't exists. `bytes` type can be used as an array of one byte each item.

  Many methods are readjusted to these conditions.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        # unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from xoutil.deprecation import deprecated as _deprecated
from xoutil.eight import _py3

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
    from xoutil.eight import text_type
    if isinstance(s, text_type):
        return s
    else:
        encoding = force_encoding(encoding)
        try:
            # In Python 3 str(b'm') returns the string "b'm'" and not just "m",
            # this fixes this.
            return text_type(s, encoding, 'replace')
        except LookupError:
            # The provided enconding is not know, try with no encoding.
            return safe_decode(s)
        except:
            # For numbers and other stuff.
            return text_type(s)


def safe_encode(u, encoding=None):
    '''Similar to unicode `encode` method returning bytes.

    Encodes `u` using the given `encoding`, or determining one from the system.

    Returning type is always `bytes`; but in python 2.x is also `str`.

    .. versionadded:: 1.1.3

    '''
    # TODO: This is not nice for Python 3, bytes is not valid string any more
    #       See :func:`json.encoder.py_encode_basestring_ascii` of Python 2.x
    from xoutil.eight import string_types, text_type
    if isinstance(u, bytes):
        return u
    else:
        encoding = force_encoding(encoding)
        try:
            try:
                if isinstance(u, string_types):
                    # In Python 2.x bytes does not allows an encoding argument.
                    return bytes(u)
                else:
                    return text_type(u).encode(encoding, 'replace')
            except:
                return text_type(u).encode(encoding, 'replace')
        except LookupError:
            return safe_encode(u)


def safe_str(obj=str()):
    '''Convert to normal string type in a safe way.

    Most of our Python 2.x code uses unicode as normal string, also in
    Python 3 converting bytes or byte-arrays to strings includes the "b"
    prefix in the resulting value.

    This function is useful in some scenarios that require `str` type (for
    example attribute ``__name__`` in functions and types).

    As ``str is bytes`` in Python2, using str(value) assures correct these
    scenarios in most cases, but in other is not enough, for example::

      >>> from xoutil.string import safe_str as sstr
      >>> def inverted_partial(func, *args, **keywords):
      ...     def inner(*a, **kw):
      ...         a += args
      ...         kw.update(keywords)
      ...         return func(*a, **kw)
      ...     inner.__name__ = sstr(func.__name__.replace('lambda', u'λ'))
      ...     return inner

    .. versionadded:: 1.7.0

    '''
    if _py3:
        if isinstance(obj, (bytes, bytearray)):
            return safe_decode(obj)
        else:
            return str(obj)
    else:
        try:
            return str(obj)
        except UnicodeEncodeError:
            # assert isinstance(value, unicode)
            return safe_encode(obj)


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
if _py3:
    safe_join = _deprecated('builtin join method of str',
                            'safe_join is deprecated for Python 3. Use '
                            'builtin join method of str.')(safe_join)


def safe_strip(value):
    '''Removes the leading and tailing space-chars from `value` if string, else
    return `value` unchanged.

    .. versionadded:: 1.1.3

    '''
    from xoutil.eight import string_types
    return value.strip() if isinstance(value, string_types) else value


def cut_prefix(value, prefix):
    '''Removes the leading `prefix` if exists, else return `value`
    unchanged.

    '''
    from xoutil.eight import text_type as str, binary_type as bytes
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
    from xoutil.eight import text_type as str, binary_type as bytes
    if isinstance(value, str) and isinstance(suffix, bytes):
        suffix = safe_decode(suffix)
    elif isinstance(value, bytes) and isinstance(suffix, str):
        suffix = safe_encode(suffix)
    # Since value.endswith('') is always true but value[:-0] is actually
    # always value[:0], which is always '', we have to explictly test for
    # len(suffix)
    if len(suffix) > 0 and value.endswith(suffix):
        return value[:-len(suffix)]
    else:
        return value


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

        >>> from xoutil.eight import text_type
        >>> type(capitalize(text_type('something'))) is text_type
        True

        >>> type(capitalize(str('something'))) is str
        True

    '''
    tstr = type(value)
    space, empty = tstr(' '), tstr('')
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


def hyphen_name(name):
    '''Convert a name, normally an identifier, to a hyphened slug.

    All transitions from lower to upper capitals (or from digits to letters)
    are joined with a hyphen.

    Also, all invalid characters (those invalid in Python identifiers) are
    converted to hyphens.

    For example::

      >>> hyphen_name('BaseNode') == 'base-node'
      True

    '''
    import re
    regex = re.compile('([a-z0-9][A-Z]|[a-zA-Z][0-9]|[0-9][a-z])')
    parts = []
    for m in reversed(list(regex.finditer(name))):
        i, f = m.span()
        name, tail = name[:i + 1], name[i + 1:]
        parts.insert(0, tail)
    parts.insert(0, name)
    name = '-'.join(parts)
    return safe_str(normalize_slug(name, '-', '_'))


# TODO: Document and fix all these "normalize_..." functions
def normalize_unicode(value):
    # FIXME: i18n
    if (value is None) or (value is str('')):
        return ''
    elif value is True:
        return safe_decode('Sí')
    elif value is False:
        return safe_decode('No')
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
    '''Return the string normal form for the `value`

    Convert all non-ascii to valid characters using unicode 'NFKC'
    normalization.

    '''
    import unicodedata
    from xoutil.eight import text_type
    if not isinstance(value, text_type):
        value = safe_decode(value)
    res = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    return safe_str(res)


def normalize_slug(value, replacement='-', invalids=None, valids=None):
    '''Return the string normal form, valid for slugs, for the `value`

    Convert all non-ascii to valid characters using unicode 'NFKC'
    normalization.

    Lower-case the result.

    Replace unwanted characters by `replacement`, repetition of given pattern
    will be converted to only one instance.

    .. warning:: There's a known bug when `replacement` contains '\'.

    ``[_a-z0-9]`` are assumed as valid characters.  Extra arguments can modify
    this standard behaviour:

    :param invalids: Any collection of characters added to these that are
           normally invalid in the provided `value`. (non-ascii or not
           included in valid characters).  Boolean ``True`` can be passed as a
           synonymous of ``"_"`` for compatibility with old
           ``invalid_underscore`` argument.  ``False`` or ``None`` are assumed
           as an empty set for invalid characters.

    :param valids: A collection of extra valid characters (all non-ascii
           characters are ignored).  This parameter could be either a valid
           string, any iterator of valid strings of characters, or ``None`` to
           use only default valid characters (See above).

    .. warning:: The result may contain characters in `invalids` if
                 `replacements` does.

    Parameters `value` and `replacement` could be of any (non-string) type,
    these values are normalized and converted to lower-case ASCII strings.

    Examples::

      >>> normalize_slug('  Á.e i  Ó  u  ') == 'a-e-i-o-u'
      True

      >>> normalize_slug('  Á.e i  Ó  u  ', '.', invalids='AU') == 'e.i.o'
      True

      >>> normalize_slug('  Á.e i  Ó  u  ', valids='.') == 'a.e-i-o-u'
      True

      >>> normalize_slug('_x', '_') == '_x'
      True

      >>> normalize_slug('-x', '_') == 'x'
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

      >>> normalize_slug('_x', '_') == '_x'
      True

    .. versionchanged:: 1.5.5 Added the `invalid_underscore` parameter.

    .. versionchanged:: 1.6.6 Replaced the `invalid_underscore` paremeter by
       `invalids`.  Added the `valids` parameter.

    .. versionchanged:: 1.7.2 Clarified the role of `invalids` with regards to
       `replacement`.

    '''
    import re
    from xoutil.eight import string_types
    # local functions
    _normalize = lambda v: normalize_ascii(v).lower()
    _set = lambda v: ''.join(set(v))
    _esc = lambda v: re.escape(_set(v))
    _from_iter = lambda v: ''.join(i for i in v)
    # check and adjust arguments
    if replacement in (None, False):
        replacement = ''
    elif isinstance(replacement, string_types):
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
        if not isinstance(invalids, string_types):
            invalids = _from_iter(invalids)
        invalids = _esc(_normalize(invalids))
    if valids is None:
        valids = ''
    else:
        if not isinstance(valids, string_types):
            valids = _from_iter(valids)
        valids = _esc(re.sub(r'[0-9a-b]+', '', _normalize(valids)))
    # calculate result
    res = _normalize(value)
    regex = re.compile(r'[^_a-z0-9%s]+' % valids)
    repl = '\t' if replacement else ''
    res = regex.sub(repl, res)
    if invalids:
        regex = re.compile(r'[%s]+' % invalids)
        res = regex.sub(repl, res)
    if repl:
        r = {'r': r'%s' % re.escape(repl)}
        regex = re.compile(r'(%(r)s){2,}' % r)
        res = regex.sub(repl, res)
        regex = re.compile(r'(^%(r)s+|%(r)s+$)' % r)
        res = regex.sub('', res)
        regex = re.compile(r'[\t]' % r)
        res = regex.sub(replacement, res)
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
    from xoutil.eight import string_types
    if isinstance(value, string_types):
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
    # TODO: Move to `xoutil.web`
    if isinstance(value, (list, tuple, set)) and len(value) > 0:
        value = value[0]
    try:
        return int(safe_strip(value))
    except:
        return default


def error2str(error):
    '''Convert an error to string.'''
    from xoutil.eight import string_types
    from xoutil.types import type_coerce
    if isinstance(error, string_types):
        return safe_str(error)
    elif isinstance(error, BaseException):
        tname = type(error).__name__
        res = safe_str(error)
        if tname in res:
            return res
        else:
            return str(': ').join(tname, res) if res else tname
    elif issubclass(error, BaseException):
        return type(error).__name__
    else:
        prefix = str('unknown error: ')
        cls = type_coerce(error)
        tname = cls.__name__
        if cls is error:
            res = tname
        else:
            res = safe_str(error)
            if tname not in res:
                res = str('{}({})').format(tname, res) if res else tname
        return prefix + res


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


from xoutil.eight import input

input = _deprecated(
    input,
    "xoutil.string.input is deprecated.  Use xoutil.eight.input"
)(input)
