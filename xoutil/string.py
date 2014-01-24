#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.string
#----------------------------------------------------------------------
# Copyright (c) 2012, 2013, 2014 Merchise Autrement and Contributors
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

from re import compile as _regex_compile

from xoutil.deprecation import deprecated as _deprecated
from xoutil.compat import (str_base as _str_base, _unicode,
                           ext_str_types as _ext_str_types,
                           py3k as _py3k)

from xoutil.modules import copy_members as _copy_python_module_members
_pm = _copy_python_module_members()

Formatter = _pm.Formatter     # Redundant but needed to avoid IDE errors

del _copy_python_module_members, _pm

__docstring_format__ = 'rst'
__author__ = 'manu'



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
    return value.strip() if isinstance(value, _ext_str_types) else value


def cut_prefix(value, prefix):
    '''Removes the leading `prefix` if exists, else return `value`
    unchanged.

    '''
    return value[len(prefix):] if value.startswith(prefix) else value


def cut_suffix(value, suffix):
    '''Removes the tailing `suffix` if exists, else return `value`
    unchanged.

    '''
    return value[:-len(suffix)] if value.endswith(suffix) else value


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


def normalize_unicode(value):
    # FIXME: i18n
    if (value is None) or (value is b''):
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
    is_bytes = isinstance(value, bytes)
    regex, sep = (b'(\S+)\s*', b' ') if is_bytes else ('(\S+)\s*', ' ')
    regex = _regex_compile(regex)
    matches = regex.findall(value)
    names = (m.capitalize() if len(m) >= 3 else m.lower() for m in matches)
    return sep.join(names)


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

if not _py3k:
    input = lambda prompt=None: safe_decode(raw_input(prompt))
    input.__doc__ = '''If the prompt argument is present, it is written to
    standard output without a trailing newline. The function then reads a line
    from input, converts it to a string (stripping a trailing newline), and
    returns that. When EOF is read, EOFError is raised. Example::

        >>> s = input('--> ')
        --> Monty Python's Flying Circus
        >>> s
        "Monty Python's Flying Circus"

    If the ``readline`` module was loaded, then :func:`input` will use it to
    provide elaborate line editing and history features.

    '''
else:
    from builtins import input
