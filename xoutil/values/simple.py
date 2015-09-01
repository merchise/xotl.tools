#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.values.simple
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-08-26

'''Simple or internal coercers.

With coercers defined in this module, many of the `xoutil.string` utilities
could be deprecated.

In Python 3, all arrays, not only those containing valid byte or unicode
chars, are buffers.


'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from . import coercer


@coercer
def name_coerce(arg):
    '''If `arg` is a named object, return its name, else `Invalid`.

    Object names are always of `str` type, other types are considered
    invalids.

    Generator objects has the special `__name__` attribute, but are ignored
    and considered invalids.

    '''
    from types import GeneratorType
    from . import Invalid
    if isinstance(arg, GeneratorType):
        return Invalid
    else:
        if isinstance(arg, (staticmethod, classmethod)):
            fn = getattr(arg, '__func__', None)
            if fn:
                arg = fn
        res = getattr(arg, '__name__', None)
        return res if isinstance(res, str) else Invalid


@coercer
def strict_iterable_coerce(arg):
    '''Return the same argument if it is a strict iterable.

    Strings are excluded.

    '''
    from xoutil.eight import string_types
    from collections import Iterable
    from . import Invalid
    ok = not isinstance(arg, string_types) and isinstance(arg, Iterable)
    return arg if ok else Invalid


@coercer
def decode_coerce(arg):
    '''Decode objects implementing the buffer protocol.'''
    import locale
    from . import Invalid
    from xoutil.eight import text_type as text, callable
    encoding = locale.getpreferredencoding() or 'UTF-8'
    decode = getattr(arg, 'decode', None)
    if callable(decode):
        try:
            res = decode(encoding, 'replace')
            if not isinstance(res, text):
                res = None
        except BaseException:
            res = None
    else:
        res = None
    if res is None:
        try:
            # TODO: All arrays are decoded, and not only those containing
            # valid byte or unicode characters.
            import codecs
            res = codecs.decode(arg, encoding, 'replace')
        except BaseException:
            res = Invalid
    return res


@coercer
def encode_coerce(arg):
    '''Encode string objects.'''
    import locale
    from . import Invalid
    from xoutil.eight import callable
    encoding = locale.getpreferredencoding() or 'UTF-8'
    encode = getattr(arg, 'encode', None)
    if callable(encode):
        try:
            res = encode(encoding, 'replace')
            if not isinstance(res, bytes):
                res = None
        except BaseException:
            res = None
    else:
        res = None
    if res is None:
        try:
            import codecs
            res = codecs.encode(arg, encoding, 'replace')
        except BaseException:
            res = Invalid
    return res


@coercer
def simple_bytes_coerce(arg):
    '''Extract possible character (bytes) from `arg`.

    There are several source types:

    - byte buffers.

    - strings.

    - integers between 0 and 0x10ffff0 (unicode set of characters).

    '''
    from xoutil.eight import _py3, integer_types
    if isinstance(arg, (bytes, bytearray)):
        return arg
    else:
        if isinstance(arg, integer_types):
            arg = (chr if _py3 else unichr)(arg)
        return encode_coerce(arg)


@coercer
def unicode_coerce(arg):
    '''Decode a buffer or any object returning unicode text.

    Uses the defined `encoding` system value.

    In Python 2.x unicode has a special type different to `str` but in Python
    3 coincide with `str` type.

    Name is used in named objects, see `name_coerce`:func: for more
    information.

    See `str_coerce`:func: to coerce to standard string type, `bytes` in
    Python 2.x and unicode (`str`) in Python 3.

    .. versionadded:: 1.7.0

    '''
    from array import array
    from . import Invalid
    from xoutil.eight import text_type as text
    aux = name_coerce(arg)
    if aux is not Invalid:
        arg = aux
    if isinstance(arg, text):
        return arg
    elif isinstance(arg, bytearray):
        arg = bytes(arg)
    elif isinstance(arg, memoryview):
        arg = arg.tobytes()
    elif isinstance(arg, array):
        try:
            return arg.tounicode()
        except BaseException:
            try:
                arg = bytes(bytearray(arg.tolist()))
            except BaseException:
                arg = str(arg)
                if str is text:
                    return arg

    res = decode_coerce(arg)
    return text(arg) if res is Invalid else res


@coercer
def bytes_coerce(arg):
    '''Encode an unicode string (or any object) returning a bytes buffer.

    Uses the defined `encoding` system value.

    In Python 2.x `bytes` coincide with `str` type, in Python 3 `str` uses
    unicode and `str` is different to `bytes`.

    There are differences if you want to obtain a buffer in Python 2.x and
    Python 3; for example, the following code obtain different results::

      >>> ba = bytes([65, 66, 67])

    In Python 2.x is obtained the string ``"[65, 66, 67]"`` and in Python 3
    ``b"ABC"``.  This function normalize these differences.

    Name is used in named objects, see `name_coerce`:func: for more
    information.

    See `str_coerce`:func: to coerce to standard string type, `bytes` in
    Python 2.x and unicode (`str`) in Python 3.

    Always returns the `bytes` type.

    .. versionadded:: 1.7.0

    '''
    from array import array
    from . import Invalid
    from xoutil.eight import text_type as text
    aux = name_coerce(arg)
    if aux is not Invalid:
        arg = aux
    if isinstance(arg, bytes):
        return arg
    elif isinstance(arg, bytearray):
        return bytes(arg)
    elif isinstance(arg, memoryview):
        return arg.tobytes()
    elif isinstance(arg, array):
        try:
            arg = arg.tounicode()
        except BaseException:
            try:
                return bytes(bytearray(arg.tolist()))
            except BaseException:
                arg = text(arg)
    res = encode_coerce(arg)
    return encode_coerce(text(arg)) if res is Invalid else res


@coercer
def str_coerce(arg):
    '''Coerce to standard string type.

    `bytes` in Python 2.x and unicode (`str`) in Python 3.

    .. versionadded:: 1.7.0

    '''
    # TODO: Analyze if promote to global::
    #   str_coerce = unicode_coerce if _py3 else bytes_coerce
    from xoutil.eight import _py3
    return (unicode_coerce if _py3 else bytes_coerce)(arg)


@coercer
def ascii_coerce(arg):
    '''Coerce to string containing only ASCII characters.

    Convert all non-ascii to valid characters using unicode 'NFKC'
    normalization.

    '''
    import unicodedata
    from xoutil.eight import text_type
    if not isinstance(arg, text_type):
        arg = unicode_coerce(arg)
    res = unicodedata.normalize('NFKD', arg).encode('ascii', 'ignore')
    return str_coerce(res)


@coercer
def ascii_set_coerce(arg):
    '''Coerce to string with only ASCII characters removing repetitions.

    Convert all non-ascii to valid characters using unicode 'NFKC'
    normalization.

    '''
    return str().join(set(ascii_coerce(arg)))


@coercer
def lower_ascii_coerce(arg):
    '''Coerce to string containing only lower-case ASCII characters.

    Convert all non-ascii to valid characters using unicode 'NFKC'
    normalization.

    '''
    return ascii_coerce(arg).lower()


@coercer
def lower_ascii_set_coerce(arg):
    '''Coerce to string with only lower-case ASCII chars removing repetitions.

    Convert all non-ascii to valid characters using unicode 'NFKC'
    normalization.

    '''
    return str().join(set(lower_ascii_coerce(arg)))
