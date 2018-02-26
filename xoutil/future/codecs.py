#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Codec registry, base classes and tools.

In this module, some additions for `codecs` standard module.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)


from codecs import *    # noqa
from codecs import __all__    # noqa
__all__ = list(__all__)


def force_encoding(encoding=None):
    '''Validates an encoding value.

    If `encoding` is None use `locale.getdefaultlocale`:func:.  If that is
    also none, return 'UTF-8'.

    .. versionadded:: 1.2.0

    .. versionchanged:: 1.8.0 migrated to 'future.codecs'

    .. versionchanged:: 1.8.7 Stop using `locale.getpreferrededencoding`:func:
       and improve documentation.

    '''
    # TODO: This mechanism is tricky, we must find out how to unroll the mess
    # involving the concept of which encoding to use by default:
    #
    # - locale.getlocale(): In Python 2 returns ``(None, None)``, but in
    #   Python 3 ``('en_US', 'UTF-8')``.
    #
    # - locale.getpreferredencoding(): all versions returns ``'UTF-8'``.
    #
    # - sys.getdefaultencoding(): In Python 2 returns ``'ascii'``, but in
    #   Python 3 ``'utf-8'``.  The same in Mac-OS. The related code was
    #   commented because these differences.
    #
    # All these considerations where also proved in Mac-OS.
    import locale
    return encoding or locale.getdefaultlocale()[1] or 'UTF-8'


def safe_decode(s, encoding=None):
    '''Similar to bytes `decode` method returning unicode.

    Decodes `s` using the given `encoding`, or determining one from the system.

    Returning type depend on python version; if 2.x is `unicode` if 3.x `str`.

    .. versionadded:: 1.1.3
    .. versionchanged:: 1.8.0 migrated to 'future.codecs'

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
        except TypeError:
            # For numbers and other stuff.
            return text_type(s)


def safe_encode(u, encoding=None):
    '''Similar to unicode `encode` method returning bytes.

    Encodes `u` using the given `encoding`, or determining one from the system.

    Returning type is always `bytes`; but in python 2.x is also `str`.

    .. versionadded:: 1.1.3
    .. versionchanged:: 1.8.0 migrated to 'future.codecs'

    '''
    # TODO: This is not nice for Python 3, bytes is not valid string any more
    #       See `json.encoder.py_encode_basestring_ascii`:func: of Python 2.x
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
            except (UnicodeError, TypeError):
                return text_type(u).encode(encoding, 'replace')
        except LookupError:
            return safe_encode(u)


__all__ += ('force_encoding', 'safe_decode', 'safe_encode')
