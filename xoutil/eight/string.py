#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Technical string handling.

Technical strings are those that requires to be instances of `str` standard
type.  See `py-string-ambiguity`:any: for more information.

This module will be used mostly as a namespace, for example::

  from xoutil.eight import string
  Foobar.__name__ = string.force(class_name)

If these functions are going to be used standalone, do something like::

  from xoutil.eight.string import force as force_str
  Foobar.__name__ = force_str(class_name)

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)


def force(value=str(), encoding=None):
    '''Convert any value to standard `str` type in a safe way.

    This function is useful in some scenarios that require `str` type (for
    example attribute ``__name__`` in functions and types).

    As ``str is bytes`` in Python 2, using str(value) assures correct these
    scenarios in most cases, but in other is not enough, for example::

      >>> from xoutil.eight import string
      >>> def inverted_partial(func, *args, **keywords):
      ...     def inner(*a, **kw):
      ...         a += args
      ...         kw.update(keywords)
      ...         return func(*a, **kw)
      ...     name = func.__name__.replace('lambda', u'λ')
      ...     inner.__name__ = string.force(name)
      ...     return inner

    .. versionchanged:: 1.9.6 Add the 'enconding' parameter.

    '''
    from xoutil.future.codecs import safe_decode, safe_encode
    if isinstance(value, str):
        return value
    elif str is bytes:      # Python 2
        return safe_encode(value, encoding=encoding)
    else:
        return safe_decode(value, encoding=encoding)


def safe_join(separator, iterable, encoding=None):
    '''Similar to `join` method in string objects.

    The semantics is equivalent to ``separator.join(iterable)`` but forcing
    separator and items to be of ``str`` standard type.

    For example::

      >>> safe_join('-', range(6))
      '0-1-2-3-4-5'

    Check that the expression ``'-'.join(range(6))`` raises a ``TypeError``.

    .. versionchanged:: 1.9.6 Add the 'enconding' parameter.

    '''
    sep = force(separator, encoding)
    return sep.join(force(item, encoding) for item in iterable)


def force_ascii(value, encoding=None):
    '''Return the string normal form for the `value`

    Convert all non-ascii to valid characters using unicode 'NFKC'
    normalization.

    :param encoding: If `value` is not a text (unicode), it is decoded before
           ASCII normalization using this encoding.  If not provided use the
           return of `~xoutil.future.codecs.force_encoding`:func:.

    .. versionchanged:: 1.8.7 Add parameter 'encoding'.

    '''
    import unicodedata
    from xoutil.future.codecs import safe_decode
    from xoutil.eight import text_type
    from xoutil.eight import string
    if not isinstance(value, text_type):
        value = safe_decode(value, encoding=encoding)
    res = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    return string.force(res)


# ------------------ Here, the original file starts ------------------

if hasattr(str, 'isidentifier'):
    def isidentifier(s):
        return str(s) if s.isidentifier() else False
else:
    import re    # noqa
    _PY2_IDENTIFIER_REGEX = re.compile('(?i)^[_a-z][_a-z0-9]*$')
    del re

    def isidentifier(s):
        return str(s) if _PY2_IDENTIFIER_REGEX.match(s) else False

isidentifier.__doc__ = ('If `s` is a valid identifier according to the '
                        'language definition.')


def isfullidentifier(s):
    '''Check if `arg` is a valid dotted Python identifier.

    See `isidentifier`:func: for what "validity" means.

    '''
    return str(s) if all(isidentifier(p) for p in s.split('.')) else False


def safe_isidentifier(s):
    '''If `s` is a valid identifier according to the language definition.

    Check before if `s` is instance of string types.

    '''
    from xoutil.eight import string_types
    return isinstance(s, string_types) and isidentifier(s)


def safe_isfullidentifier(s):
    '''Check if `arg` is a valid dotted Python identifier.

    Check before if `s` is instance of string types.  See
    `safe_isidentifier`:func: for what "validity" means.

    '''
    from xoutil.eight import string_types
    return isinstance(s, string_types) and isfullidentifier(s)


def check_identifier(s):
    '''Check if `s` is a valid identifier.'''
    from xoutil.eight.string import isidentifier
    res = isidentifier(s)
    if res:
        return res
    else:
        msg = 'invalid identifier "{}"'
        raise TypeError(msg.format(s))
