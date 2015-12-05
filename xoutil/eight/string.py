#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight.string
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-10-29

'''Checkers for simple types depending on differences between Python 2 and 3.

.. versionadded:: 1.7.1

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


try:
    from keyword import kwlist, iskeyword    # noqa
    kwlist = frozenset(kwlist)
except ImportError:
    # XXX: Next keyword-list could be wrong because If any keywords are
    # defined to only be active when particular `__future__` statements are in
    # effect -or removed, like `print`-, these must be included or removed as
    # well.
    kwlist = frozenset(['False', 'None', 'True', 'and', 'as', 'assert',
                        'break', 'class', 'continue', 'def', 'del', 'elif',
                        'else', 'except', 'exec', 'finally', 'for', 'from',
                        'global', 'if', 'import', 'in', 'is', 'lambda',
                        'not', 'or', 'pass', 'print', 'raise', 'return',
                        'try', 'while', 'with', 'yield'])

    def iskeyword(s):
        '''Return true if `s` is a Python keyword.'''
        return s in kwlist


from re import compile as regex_compile

_PY2_IDENTIFIER_REGEX = regex_compile('(?i)^[_a-z][_a-z0-9]*$')

del regex_compile


if hasattr(str, 'isidentifier'):
    def isidentifier(s):
        return str(s) if s.isidentifier() else False
else:
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
    from . import string_types
    return isinstance(s, string_types) and isidentifier(s)


def safe_isfullidentifier(s):
    '''Check if `arg` is a valid dotted Python identifier.

    Check before if `s` is instance of string types.  See
    `safe_isidentifier`:func: for what "validity" means.

    '''
    from .. import string_types
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
