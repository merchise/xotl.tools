#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.future.string
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~] and Contributors
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
# Created on 2012-02-17
# Migrated to 'future' on 2016-09-20

'''Some additions for `string` standard module.

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
                        absolute_import as _py3_abs_imports)

from string import *    # noqa
import string as _stdlib    # noqa

try:
    from string import __all__    # noqa
    __all__ = list(__all__)
except ImportError:
    # Python 2 and PyPy don't implement '__all__' for 'string' module.
    __all__ = [name for name in dir(_stdlib) if not name.startswith('_')]

from xoutil.future import _past
_past.dissuade()
del _past

from xoutil.deprecation import deprecated    # noqa
from xoutil.deprecation import inject_deprecated    # noqa
from xoutil.eight import python_version    # noqa


# TODO: In Python 2.x series, equal comparison for `unicode` an `str` types
# don't ever match.  For example::
#   >>> s = 'λ'
#   >>> u = u'λ'
#   >>> u == s
#   False
#
# Also a `UnicodeWarning` is issued with message "Unicode equal comparison
# failed to convert both arguments to Unicode - interpreting them as being
# unequal.  This must be fixed in this module.


ELLIPSIS_ASCII = '...'
ELLIPSIS_UNICODE = '…'

#: Value used as a fill when a string representation is brimmed over.
ELLIPSIS = ELLIPSIS_UNICODE if python_version == 3 else ELLIPSIS_ASCII

#: Default value for `max_width` parameter in functions that reduce strings,
#: see `crop`:func: and `small`:func:.
DEFAULT_MAX_WIDTH = 64

#: Value for `max_width` parameter in functions that reduce strings, must not
#: be less than this value.
MIN_WIDTH = 8

import xoutil.future.codecs      # noqa

inject_deprecated(('force_encoding', 'safe_decode', 'safe_encode'),
                  xoutil.future.codecs)


def safe_str(obj=str()):
    '''Convert to normal string type in a safe way.

    Most of our Python 2.x code uses unicode as normal string, also in
    Python 3 converting bytes or byte-arrays to strings includes the "b"
    prefix in the resulting value.

    This function is useful in some scenarios that require `str` type (for
    example attribute ``__name__`` in functions and types).

    As ``str is bytes`` in Python2, using str(value) assures correct these
    scenarios in most cases, but in other is not enough, for example::

      >>> from xoutil.future.string import safe_str as sstr
      >>> def inverted_partial(func, *args, **keywords):
      ...     def inner(*a, **kw):
      ...         a += args
      ...         kw.update(keywords)
      ...         return func(*a, **kw)
      ...     inner.__name__ = sstr(func.__name__.replace('lambda', u'λ'))
      ...     return inner

    .. versionadded:: 1.7.0

    '''
    if python_version == 3:
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
    '''Similar to `join` method in string objects.

    The semantics is quivalent to ``separator.join(iterable)``.

    Return a string which is the concatenation of the strings in the
    `iterable`.  The `separator` between elements is the first argument.

    The return type could be `unicode` or `bytes` depending on the `separator`
    type, and the type of each item in the `iterable`.

    Param `encoding` is used in case of error to concatenate `bytes` +
    `unicode`.

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
if python_version == 3:
    safe_join = deprecated('builtin join method of str',
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


def hyphen_name(name, join_numbers=True):
    '''Convert a name to a hyphened slug.

    The name is normally an identifier in Camel-Case.

    Also, all invalid characters (those invalid in Python identifiers) are
    ignored.  Numbers are joined with preceding part when `join_numbers` is
    True.

    For example::

      >>> hyphen_name('BaseNode') == 'base-node'
      True

      >>> hyphen_name('ICQNámeAc3P123') == 'icq-name-ac3-p123'
      True

      >> hyphen_name('--__ICQNámeP12_34Abc--') == 'icq-name-p12-34-abc'
      True

      >> hyphen_name('ICQNámeP12', join_numbers=False) == 'icq-name-p-12'
      True

    '''
    import re
    name = normalize_ascii(name)
    regex = re.compile('[^A-Za-z0-9]+')
    name = regex.sub('-', name)
    regex = re.compile('([A-Z]+|[a-z]+|[0-9]+|-)')
    all = regex.findall(name)
    i, count, parts = 0, len(all), []
    while i < count:
        part = all[i]
        if part != '-':
            upper = 'A' <= part <= 'Z'
            if upper:
                part = part.lower()
            j = i + 1
            if j < count and upper and 'a' <= all[j] <= 'z':
                aux = part[:-1]
                if aux:
                    parts.append(aux)
                part = part[-1] + all[j]
                i = j
                j += 1
            if j < count and '0' <= all[j] <= '9' and join_numbers:
                part = part + all[j]
                i = j
            parts.append(part)
        i += 1
    return '-'.join(parts)


# TODO: Document and fix all these "normalize_..." functions
def normalize_unicode(value):
    # TODO: Deprecate
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
    # TODO: Deprecate
    return capitalize(normalize_unicode(value))


def normalize_title(value):
    # TODO: Deprecate
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


# TODO: It's probable that there are more than one 'slug' functions.  Also,
# this function is more proper in a module named 'identifier', or something.
def normalize_slug(value, *args, **kwds):
    '''Return the normal-form of a given string value that is valid for slugs.

    Convert all non-ascii to valid characters, whenever possible, using
    unicode 'NFKC' normalization and lower-case the result.  Replace unwanted
    characters by the value of `replacement`.

    Default valid characters are ``[_a-z0-9]``.  Extra arguments
    `invalid_chars` and `valid_chars` can modify this standard behaviour, see
    next:

    :param value: The value to normalize (a not empty string).

    :param replacement: Normally a one character string to use in place of
           invalid parts.  Repeated instances of the replacement will be
           converted to just one; if appearing at the beginning or at the end,
           are striped.  The value of this argument not contain any in
           `invalid_chars` (a contradiction).  If ``None`` or ``False``, it is
           converted to an empty string for backward compatibility with old
           versions of this function.

    :param invalid_chars: Any collection of characters added to these that are
           normally invalid (non-ascii or not included in valid characters).
           Boolean ``True`` can be passed as a synonymous of ``"_"`` for
           compatibility with old ``invalid_underscore`` argument.  ``False``
           or ``None`` are assumed as an empty set for invalid characters.  If
           given as a positional argument, must be the second in the `args`
           tuple.  Default value is ``""``.

    .. todo:: check if "valid" plural is without "s" in English.

    :param valid_chars: A collection of extra valid characters.  Could be
           either a valid string, any iterator of strings, or ``None`` to use
           only default valid characters.  Non-ASCII characters are ignored.

    Examples::

      >>> normalize_slug('  Á.e i  Ó  u  ') == 'a-e-i-o-u'
      True

      >>> normalize_slug(' Á.e i  Ó  u  ', '.', invalid_chars='AU') == 'e.i.o'
      True

      >>> normalize_slug('  Á.e i  Ó  u  ', valid_chars='.') == 'a.e-i-o-u'
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

      >>> normalize_slug(123456, '', invalid_chars='52') == '1346'
      True

      >>> normalize_slug('_x', '_') == '_x'
      True

    .. versionchanged:: 1.5.5 Added the `invalid_underscore` parameter.

    .. versionchanged:: 1.6.6 Replaced the `invalid_underscore` paremeter by
       `invalids`.  Added the `valids` parameter.

    .. versionchanged:: 1.7.2 Clarified the role of `invalids` with regards to
       `replacement`.

    .. versionchanged:: 1.8.0 Deprecate the `invalids` paremeter name in favor
       of `invalid_chars`, also deprecate the `valids` paremeter name in favor
       of `valid_chars`.

    '''
    import re
    from xoutil.eight import string_types
    from xoutil.params import ParamManager

    from xoutil.cl import compose, istype
    from xoutil.cl.simple import not_false, ascii_coerce

    _str = compose(not_false(''), istype(string_types))
    _ascii = compose(_str, ascii_coerce)
    _set = compose(_ascii, lambda v: ''.join(set(v)))

    # local functions
    def _normalize(v):
        return normalize_ascii(v).lower()

    def _set(v):
        return re.escape(''.join(set(_normalize(v))))

    getarg = ParamManager(args, kwds)
    replacement = getarg('replacement', 0, default='-', coercers=string_types)
    # TODO: deprecate 'invalids' and 'valids' names.
    invalid_chars = getarg('invalid_chars', 'invalid', 'invalids', 0,
                           default='', coercers=_ascii)
    valid_chars = getarg('valid_chars', 'valid', 'valids', 0, default='',
                         coercers=_ascii)
    replacement = args[0] if args else kwds.pop('replacement', '-')
    # TODO: check unnecessary arguments, raising errors
    if replacement in (None, False):
        # for backward compatibility
        replacement = ''
    elif isinstance(replacement, string_types):
        replacement = _normalize(replacement)
    else:
        msg = ('normalize_slug() "replacement" ({}) must be a string or '
               'None, not "{}".')
        raise TypeError(msg.format(replacement, type(replacement)))
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
            msg = ('normalize_slug() replacement "{}" must not contain any '
                   'character in the invalid set.')
            raise ValueError(msg.format(replacement))
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
    from xoutil.eight import force_type, type_name
    if isinstance(error, string_types):
        return safe_str(error)
    elif isinstance(error, BaseException):
        tname = type_name(error)
        res = safe_str(error)
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
                     `safe_encode`:func: or :func:`safe_decode`.

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


def _check_max_width(max_width, caller=None):
    '''Used internally by some functions.'''
    if max_width is None:
        max_width = DEFAULT_MAX_WIDTH
    elif max_width < MIN_WIDTH:
        msg = '{}() '.format(caller) if caller else ''
        msg += ('invalid value for `max_width`, must be between greated than '
                '{}; got {}').format(MIN_WIDTH, max_width)
        raise ValueError(msg)
    return max_width


def crop(obj, max_width=None):
    '''Return a reduced string representation of `obj`.

    Classes can now define a new special method or attribute named
    '__crop__'.

    If `max_width` is not given, defaults to ``DEFAULT_MAX_WIDTH``.

    .. versionadded:: 1.8.0

    '''
    from xoutil.eight import callable, type_name, string_types
    max_width = _check_max_width(max_width, caller='crop')
    if isinstance(obj, string_types):
        res = obj    # TODO: reduce
    elif hasattr(obj, '__crop__'):
        aux = obj.__crop__
        if isinstance(aux, string_types):
            res = aux
        elif callable(aux):
            if getattr(aux, '__self__', 'ok') is not None:
                res = aux()
            else:
                res = None
        else:
            msg = "crop() invalid '__crop__' type: {}"
            raise TypeError(msg.format(type_name(aux)))
    else:
        res = None
    if res is None:
        res = _crop(obj, max_width)
    return res


def _crop(obj, max_width):
    '''Internal tool for `crop`:func:.'''
    from collections import Set, Mapping
    from xoutil.eight import type_name
    res = str(obj)
    if (res.startswith('<') and res.endswith('>')) or len(res) > max_width:
        try:
            res = obj.__name__
        except AttributeError:
            if isinstance(obj, (tuple, list, Set, Mapping)):
                res = crop_iterator(obj, max_width)
            else:
                res = '{}({})'.format(type_name(obj), ELLIPSIS)
    return res


def crop_iterator(obj, max_width=None):
    '''Return a reduced string representation of the iterator `obj`.

    See `crop`:func: function for a more general tool.

    If `max_width` is not given, defaults to ``DEFAULT_MAX_WIDTH``.

    .. versionadded:: 1.8.0

    '''
    from collections import Set, Mapping
    from xoutil.eight import type_name
    max_width = _check_max_width(max_width, caller='crop_iterator')
    classes = (tuple, list, Mapping, Set)
    cls = next((c for c in classes if isinstance(obj, c)), None)
    if cls:
        res = ''
        if cls is Set and not obj:
            borders = ('{}('.format(type_name(obj)), ')')
        else:
            borders = ('()', '[]', '{}', '{}')[classes.index(cls)]
            UNDEF = object()
            sep = ', '
            if cls is Mapping:
                from xoutil.eight import iteritems

                def itemrepr(item):
                    key, value = item
                    return '{}: {}'.format(repr(key), repr(value))
            else:
                iteritems = iter
                itemrepr = repr
            items = iteritems(obj)
            ok = True
            while ok:
                item = next(items, UNDEF)
                if item is not UNDEF:
                    if res:
                        res += sep
                    aux = itemrepr(item)
                    if len(res) + len(borders) + len(aux) <= max_width:
                        res += aux
                    else:
                        res += ELLIPSIS
                        ok = False
                else:
                    ok = False
        return '{}{}{}'.format(borders[0], res, borders[1])
    else:
        raise TypeError('crop_iterator() expects tuple, list, set, or '
                        'mapping; got {}'.format(type_name(obj)))


def small(obj, max_width=None):
    '''Crop the string representation of `obj` and make some replacements.

    - Lambda function representations ('<lambda>' by 'λ').

    - Ellipsis ('...'  by '…')

    If max_width is not given, defaults to ``DEFAULT_MAX_WIDTH``.

    .. versionadded:: 1.8.0

    '''
    max_width = _check_max_width(max_width, caller='small')
    res = crop(obj, max_width)
    res = res.replace(ELLIPSIS_ASCII, ELLIPSIS_UNICODE)
    res = res.replace((lambda: None).__name__, 'λ')
    return res


from xoutil.eight import input    # noqa

input = deprecated(input, "xoutil.future.string.input is deprecated.  Use "
                   "xoutil.eight.input")(input)

del deprecated

__all__ += ['force_encoding', 'safe_decode', 'safe_encode', 'safe_str',
            'safe_join', 'safe_strip', 'cut_prefix', 'cut_any_prefix',
            'cut_prefixes', 'cut_suffix', 'cut_any_suffix', 'cut_suffixes',
            'capitalize_word', 'capitalize', 'hyphen_name',
            'normalize_unicode', 'normalize_name', 'normalize_title',
            'normalize_str', 'normalize_ascii', 'normalize_slug',
            'strfnumber', 'parse_boolean', 'parse_url_int', 'error2str',
            'force_str', 'make_a10z', 'crop', crop_iterator, small]
