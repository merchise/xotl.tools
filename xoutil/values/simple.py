#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.values.simple
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
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
    from xoutil.eight import text_type, callable
    encoding = locale.getpreferredencoding() or 'UTF-8'
    decode = getattr(arg, 'decode', None)
    if callable(decode):
        try:
            res = decode(encoding, 'replace')
            if not isinstance(res, text_type):
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
    from xoutil.eight import text_type
    aux = name_coerce(arg)
    if aux is not Invalid:
        arg = aux
    if isinstance(arg, text_type):
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
                if str is text_type:
                    return arg

    res = decode_coerce(arg)
    return text_type(arg) if res is Invalid else res


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
    from xoutil.eight import text_type
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
                arg = text_type(arg)
    res = encode_coerce(arg)
    return encode_coerce(text_type(arg)) if res is Invalid else res


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


def chars_coerce(arg):
    '''Convert to unicode characters.

    If `arg` is an integer between ``0`` and ``0x10ffff`` is converted
    assuming it as ordinal unicode code, else is converted with
    `unicode_coerce`:meth:.

    '''
    from xoutil.eight import _py3, integer_types as ints
    if isinstance(arg, ints) and 0 <= arg <= 0x10ffff:
        return (chr if _py3 else unichr)(arg)
    else:
        return unicode_coerce(arg)


from xoutil.eight import text_type as text


class text(text):
    '''Return a nice text representation of one object.

    text(obj='') -> text

    text(bytes_or_buffer[, encoding[, errors]]) -> text

    Create a new string object from the given object.  If `encoding` or
    `errors` is specified, then the object must expose a data buffer that will
    be decoded using the given encoding and error handler.  Otherwise, returns
    the result of object text representation.

    :param encoding: defaults to ``sys.getdefaultencoding()``.

    :param errors: defaults to 'strict'.

    Method join is improved, in order to receive any collection of objects,
    as variable number of arguments or as one iterable.

    '''
    def __new__(cls, obj='', *args, **kwargs):
        if not (args or kwargs):
            obj = unicode_coerce(obj)
        return super(text, cls).__new__(cls, obj, *args, **kwargs)

    def join(self, *args):
        '''S.join(variable_number_args or iterable) -> text

        Return a text which is the concatenation of the objects (converted to
        text) in argument items.  The separator between elements is `S`.

        See `chr_join`:meth: for other vertion of this functionality.

        '''
        return self._join(unicode_coerce, args)

    def chr_join(self, *args):
        '''S.chr_join(variable_number_args or iterable) -> text

        Return a text which is the concatenation of the objects (converted to
        text) in argument items.  The separator between elements is `S`.

        Difference with `join`:meth: is that integers between ``0`` and
        ``0x10ffff`` are converted to characters as unicode ordinal.

        '''
        return self._join(chars_coerce, args)

    def _join(self, coercer, args):
        '''Protected method to implement `join`:meth: and `chr_join`:meth:.'''
        from collections import Iterable
        if len(args) == 1 and isinstance(args[0], Iterable):
            args = args[0]
        return super(text, self).join(coercer(obj) for obj in args)
