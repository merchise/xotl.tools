#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.stringutil
#----------------------------------------------------------------------
# Copyright (c) 2012 Medardo Rodríguez
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

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from string import *

from re import compile as _regex_compile

from xoutil.deprecation import deprecated


__docstring_format__ = 'rst'
__author__ = 'manu'



def safe_strip(value):
    '''
    Removes the leading and trailing space-chars from value if string
    '''
    return value.strip() if isinstance(value, basestring) else value


def cut_prefix(value, prefix):
    return value[len(prefix):] if value.startswith(prefix) else value


def cut_suffix(value, suffix):
    return value[:-len(suffix)] if value.endswith(suffix) else value


def capitalize_word(value):
    'Capitalizes the first char of value'
    if value and value[0].islower():
        value = value[0].upper() + value[1:]
    return value


def capitalize(value, title=True):
    '''
    Capitalizes value according to whether it should be title-like.

    Title-like means it will capitalize every word but the 3-letters or less
    unless its the first word::

        >>> capitalize('a group is its own worst enemy')
        'A Group is its own Worst Enemy'

    (This may be odd because, in the example above, own should be capitalized.)

    If value is an unicode string, it will return a unicode string; if its a
    bytestring, then it will return a bytestring.

        >>> type(capitalize(u'something')) is unicode
        True

        >>> type(capitalize('something')) is str
        True
    '''
    space, empty = (u' ', u'') if isinstance(value, unicode) else (b' ', b'')
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
        return u''
    elif value is True:
        return u'Sí'
    elif value is False:
        return u'No'
    elif not isinstance(value, basestring):
        return unicode(value)
    elif isinstance(value, str):
        return value.decode('UTF-8')
    else:
        return value


def normalize_name(value):
    return capitalize(normalize_unicode(value))


def normalize_title(value):
    return capitalize(normalize_unicode(value), True)



_REGEX_NORMALIZE_STR = _regex_compile(b'(\S+)\s*')

def normalize_str(value):
    matches = _REGEX_NORMALIZE_STR.findall(value)
    names = []
    for match in matches:
        names.append(match.capitalize() if len(match) >= 3 else match.lower())
    return ' '.join(names)



def strfnumber(number, format='%0.2f'):
    res = format % number
    if '.' in res:
        res = res.rstrip('0')
        if res.endswith('.'):
            res = res[:-1]
    return res



def parse_boolean(value):
    '''
    Parse a boolean from any value given a special treatment to strings.

    >>> parse_boolean('trUe')
    True

    >>> parse_boolean('faLSe')
    False
    '''
    if isinstance(value, basestring):
        value = value.strip()
        if value:
            return bool(int(value)) if value.isdigit() else (value.lower() != 'false')
        else:
            return False
    else:
        return bool(value)


def parse_url_int(value, default=None):
    '''
    Parse an integer URL argument. Some operations treat simple arguments
    as a list of one element.
    '''
    if isinstance(value, (list, tuple, set)) and len(value) > 0:
        value = value[0]
    try:
        return int(safe_strip(value))
    except:
        return default


def normalize_to_str(value, encoding='utf-8'):
    if type(value) is str:
        return value
    elif type(value) is unicode:
        return value.encode(encoding)

as_str = deprecated('xoutil.stringutil.normalize_to_str')(normalize_to_str)
