#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Python 2 and Python 3 compatibility.

The name comes from (Manu's idea') "2 raised to the power of 3".

There is an existing library written by "Benjamin Peterson" named six_, both
(`xoutil.eight` and `six`) can be used together since this module don't claim
to be a replacement of six_, just some extra extensions.  Nevertheless, there
are some simple definitions that even when are in six_ also are defined here.

This package also fixes some issues from PyPy interpreter.

.. _six: https://pypi.python.org/pypi/six

'''
from xoutil.versions import python_version


try:
    from hashlib import sha1 as sha    # noqa
except ImportError:
    from sha import sha    # noqa

base_string = str
string_types = (str, )
integer_types = int,
long_int = int
class_types = type,
text_type = str
unichr = chr

binary_type = bytes
UnicodeType = text_type
StringTypes = string_types

#: Define a tuple with both base types in Python 2 and containing only `type`
#: in Python 3.
ClassTypes = class_types


# The `memoryview`:class: API is similar but not exactly the same as that
# of `buffer`.
buffer = memoryview


# Python versions

_pyver = python_version.to_float()
_py2 = python_version == 2
_py3 = python_version == 3
_py33 = python_version >= 3.3
_py34 = python_version >= 3.4
_pypy = python_version.pypy


typeof = type


def force_type(obj):
    '''Ensure return a valid type from `obj`.

    If `obj` is already a "type", return itself, else obtain its type.

    '''
    return obj if isinstance(obj, class_types) else typeof(obj)


def type_name(obj):
    '''Return the type name.'''
    return typeof(obj).__name__


from sys import intern  # noqa

input = input
range = range
ascii = ascii    # noqa
hex, oct, filter, map, zip = hex, oct, filter, map, zip


def iterkeys(d):
    '''Return an iterator over the keys of a dictionary.'''
    return iter((d.keys if _py3 else d.iterkeys)())


def itervalues(d):
    '''Return an iterator over the values of a dictionary.'''
    return iter((d.values if _py3 else d.itervalues)())


def iteritems(d):
    '''Return an iterator over the (key, value) pairs of a dictionary.'''
    return iter((d.items if _py3 else d.iteritems)())


from io import StringIO  # noqa

import builtins    # noqa
__builtin__ = builtins


callable = getattr(__builtin__, 'callable')    # noqa
exec_ = getattr(builtins, 'exec')    # noqa


def execfile(filename, globals=None, locals=None):
    """Read and execute a Python script from a file.

    The globals and locals are dictionaries, defaulting to the current
    globals and locals.  If only globals is given, locals defaults to it.

    """
    import sys
    if globals is None:
        frame = sys._getframe(1)
        globals = frame.f_globals
        if locals is None:
            locals = frame.f_locals
        del frame
    elif locals is None:
        locals = globals
    with open(filename, "r") as f:
        source = f.read()
        code = compile(source, filename, 'exec')
        return exec_(code, globals, locals)
