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


_REGEX_NORMALIZE_STR = _regex_compile(b'(\S+)\s*')


def safe_decode(s, encoding=None):
    '''
    Similar to str "decode" method returning unicode.
    Decodes "s" using the codec registered for "encoding".

    .. versionadded:: 1.1.3
    '''
    if isinstance(s, unicode):
        return s
    else:
        try:
            return unicode(s)
        except:
            import sys
            encoding = encoding or sys.stdin.encoding\
                                or sys.getdefaultencoding()
            return str(s).decode(encoding, 'replace')



def safe_encode(u, encoding=None):
    '''
    Similar to unicode "encode" method returning srt.
    Encodes "u" using the codec registered for "encoding".

    .. versionadded:: 1.1.3
    '''
    if isinstance(u, str):
        return u
    else:
        try:
            return str(u)
        except:
            import sys
            encoding = encoding or sys.stdin.encoding\
                                or sys.getdefaultencoding()
            return unicode(u).encode(encoding, 'replace')



def safe_join(separator, iterable, encoding='utf-8',
              force_separator_type=False):
    '''
    Similar to "join" method in str objects `separator.join(iterable)` but
    return "unicode" or "str" depending on type of "separator" and each item
    in  "iterable".

    Return a string which is the concatenation of the strings in the
    "iterable" with "separator" as intermediate between elements.

    "encoding" is used in case of error to concatenate str + unicode.

    "force_separator_type" only apply on error contexts.

    This function must be deprecated in Python 3.

    .. versionadded:: 1.1.3
    '''
    try:
        sep_is_unicode = isinstance(separator, unicode)
    except NameError:
        return separator.join(iterable)    # Python 3 doesn't have unicode type
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
                    if sep_is_unicode or not force_separator_type:
                        transf = safe_decode
                    else:
                        transf = safe_encode
                    res = transf(res, encoding)
                    res += transf(tail, encoding)
    return res if not empty else type(separator)()



def safe_strip(value):
    '''
    Removes the leading and trailing space-chars from value if it's a string.

    .. versionadded:: 1.1.3
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



def normalize_str(value):
    matches = _REGEX_NORMALIZE_STR.findall(value)
    names = []
    for match in matches:
        names.append(match.capitalize() if len(match) >= 3 else match.lower())
    return ' '.join(names)



def strfnumber(number, format_spec='%0.2f'):
    res = format_spec % number
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
            return bool(int(value)) if value.isdigit() \
                                            else (value.lower() != 'false')
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



class SafeFormatter(Formatter):
    '''
    Similar to original Formatter but allowing several extensions:

    - Configure initial mappings as constructor parameters.
    - Use "eval" function for keys not validated in standards ways.
    - Use safe instead standard join for return formated value.

    You can try for example::

        >>> f = SafeFormatter(x=1, y=2)
        >>> print(f.format('CWD: "{cwd}"; "x+d["x"]": {x+d["x"]}.',
        ...                cwd=b'~/tmp/foóbar', d=dict(x=1)))
        CWD: "~/tmp/foóbar"; "x+d["x"]": 2.

    .. versionadded:: 1.1.3
    '''

    USE_EVAL = True

    def __init__(self, *mappings, **kwargs):
        '''
        Initialize the formatter with several mapping objects.

        All mappings are considered at this level as "with permanent values",
        if dynamic mapping update is desired, redefine "_get_mapping" method.

        For use a list of dynamic mappings to evaluate each one separately use
        "_get_dynamic_mappings" returning any iterable; this last feature will
        never use the "eval" option.
        '''
        super(SafeFormatter, self).__init__()
        for mapping in mappings:
            kwargs.update(mapping)
        self.mapping = kwargs


    def get_value(self, key, args, kwargs):
        '''
        Use additional mappings, "eval" function and dynamic mappings.
        '''
        try:
            return super(SafeFormatter, self).get_value(key, args, kwargs)
        except:
            pass
        mapping = self._get_mapping()
        try:
            return mapping[key]
        except:
            pass
        if self.USE_EVAL:
            try:
                return eval(key, mapping, kwargs)
            except:
                pass
        for dmap in self._get_dynamic_mappings():
            if key in dmap:
                return dmap[key]
        return '<ERROR: `%s`?>' % key


    def _vformat(self, format_string, args, kwargs, used_args,
                 recursion_depth):
        '''
        Mostly copied from original but use safe instead standard join.
        '''
        if recursion_depth < 0:
            raise ValueError('Max string recursion exceeded')
        result = []
        for literal_text, field_name, format_spec, conversion in \
                                                    self.parse(format_string):
            # output the literal text
            if literal_text:
                result.append(literal_text)
            # if there's a field, output it
            if field_name is not None:
                # this is some markup, find the object and do the formatting
                # given the field_name, find the object it references and the
                # argument it came from
                obj, arg_used = self.get_field(field_name, args, kwargs)
                used_args.add(arg_used)
                # do any conversion on the resulting object
                obj = self.convert_field(obj, conversion)
                # expand the format spec, if needed
                format_spec = self._vformat(format_spec, args, kwargs,
                                            used_args, recursion_depth-1)
                # format the object and append to the result
                result.append(self.format_field(obj, format_spec))
        res = safe_join('', result)
        return res


    def format_field(self, value, format_spec):
        '''
        If standard "format" fails, use safe decoding.
        '''
        try:
            return format(value, format_spec)
        except:
            pass
        value = safe_decode(value)
        format_spec = safe_decode(format_spec)
        return format(value, format_spec)


    def _get_mapping(self):
        '''
        Redefine this in order to include dynamic mappings.
        '''
        return self.mapping


    def _get_dynamic_mappings(self):
        return ()
