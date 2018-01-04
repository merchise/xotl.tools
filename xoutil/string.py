#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Some additions for `string` standard module.

In this module `str` and `unicode` types are not used because Python 2 and
Python 3 treats strings differently (see `py-string-ambiguity`:any: for more
information).  The types `bytes` and `text_type` will be used instead with the
following conventions:

- In Python 2 `str` is synonym of `bytes` and both (`unicode` and 'str') are
  both string types inheriting form `basestring`.

- In Python 3 `str` is always unicode but `unicode` and `basestring` types
  doesn't exists.  `bytes` type can be used as an array of one byte each item.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)


from xoutil.deprecation import deprecated    # noqa
from xoutil.deprecation import import_deprecated    # noqa


_MIGRATED_TO_CODECS = ('force_encoding', 'safe_decode', 'safe_encode')

import_deprecated('xoutil.eight', 'input')
import_deprecated('xoutil.future.codecs', *_MIGRATED_TO_CODECS)
import_deprecated('xoutil.eight.string', 'safe_join', force_str='force')

safe_str = force_str    # noqa


@deprecated
def safe_strip(value):
    '''Removes the leading and tailing space-chars from `value` if string, else
    return `value` unchanged.

    '''
    from xoutil.eight import string_types
    return value.strip() if isinstance(value, string_types) else value


# TODO: Functions starting with 'cut_' must be reviewed, maybe migrated to
# some module dedicated to "string trimming".
def cut_prefix(value, prefix):
    '''Removes the leading `prefix` if exists, else return `value`
    unchanged.

    '''
    from xoutil.eight import text_type as str, binary_type as bytes
    from xoutil.future.codecs import safe_encode, safe_decode
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
    from xoutil.future.codecs import safe_decode, safe_encode
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


def slugify(value, *args, **kwds):
    '''Return the normal-form of a given string value that is valid for slugs.

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
           `ASCII normalization <xoutil.eight.string.force_ascii>`:func:.

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

    '''
    import re
    from xoutil.eight import string_types
    from xoutil.eight.string import force_ascii
    from xoutil.params import ParamManager

    from xoutil.values import compose, istype
    from xoutil.values.simple import not_false, ascii_coerce

    _str = compose(not_false(''), istype(string_types))
    _ascii = compose(_str, ascii_coerce)
    _set = compose(_ascii, lambda v: ''.join(set(v)))

    # local functions
    def _normalize(v):
        return force_ascii(v, encoding=encoding).lower()

    def _set(v):
        return re.escape(''.join(set(_normalize(v))))

    getarg = ParamManager(args, kwds)
    replacement = getarg('replacement', 0, default='-', coercers=string_types)
    invalid_chars = getarg('invalid_chars', 'invalid', 'invalids', 0,
                           default='', coercers=_ascii)
    valid_chars = getarg('valid_chars', 'valid', 'valids', 0, default='',
                         coercers=_ascii)
    encoding = getarg('encoding', default=None)
    replacement = args[0] if args else kwds.pop('replacement', '-')
    # TODO: check unnecessary arguments, raising errors
    if replacement in (None, False):
        # for backward compatibility
        replacement = ''
    elif isinstance(replacement, string_types):
        replacement = _normalize(replacement)
    else:
        raise TypeError('slugify() replacement "{}" must be a string or None,'
                        ' not "{}".'.format(replacement, type(replacement)))
    if invalid_chars is True:
        # Backward compatibility with former `invalid_underscore` argument
        invalid_chars = '_'
    elif invalid_chars in {None, False}:
        invalid_chars = ''
    else:
        if not isinstance(invalid_chars, string_types):
            invalid_chars = ''.join(invalid_chars)
        invalid_chars = _set(invalid_chars)
    if invalid_chars:
        invalid_regex = re.compile(r'[{}]+'.format(invalid_chars))
        if invalid_regex.search(replacement):
            raise ValueError('slugify() replacement "{}" must not contain '
                             'any invalid character.'.format(replacement))
    else:
        invalid_regex = None
    if valid_chars is None:
        valid_chars = ''
    else:
        if not isinstance(valid_chars, string_types):
            valid_chars = ''.join(valid_chars)
        valid_chars = _set(valid_chars)
        valid_chars = _set(re.sub(r'[0-9a-z]+', '', valid_chars))
    valid_chars = re.compile(r'[^_0-9a-z{}]+'.format(valid_chars))
    # calculate result
    repl = '\t' if replacement else ''
    res = valid_chars.sub(repl, _normalize(value))
    if invalid_regex:
        res = invalid_regex.sub(repl, res)
    if repl:
        # convert two or more replacements in only one instance
        r = r'{}'.format(re.escape(repl))
        res = re.sub(r'({r}){{2,}}'.format(r=r), repl, res)
        # remove start and end more replacement instances
        res = re.sub(r'(^{r}+|{r}+$)'.format(r=r), '', res)
        res = re.sub(r'[\t]', replacement, res)
    return res


def error2str(error):
    '''Convert an error to string.'''
    from xoutil.eight import string_types
    from xoutil.eight import force_type, type_name
    from xoutil.eight import string
    if isinstance(error, string_types):
        return string.force(error)
    elif isinstance(error, BaseException):
        tname = type_name(error)
        res = string.force(error)
        if tname in res:
            return res
        else:
            return str(': ').join(tname, res) if res else tname
    elif issubclass(error, BaseException):
        return type_name(error)
    else:
        prefix = str('unknown error: ')
        cls = force_type(error)
        tname = cls.__name__
        if cls is error:
            res = tname
        else:
            res = string.force(error)
            if tname not in res:
                res = str('{}({})').format(tname, res) if res else tname
        return prefix + res


def make_a10z(string):
    '''Utility to find out that "internationalization" is "i18n".

    Examples::

       >>> print(make_a10z('parametrization'))
       p13n
    '''
    return string[0] + str(len(string[1:-1])) + string[-1]


@deprecated(slugify)
def normalize_slug(value, *args, **kwds):
    return slugify(value, *args, **kwds)


del deprecated, import_deprecated
