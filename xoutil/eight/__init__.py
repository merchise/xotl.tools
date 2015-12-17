#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2015-02-26

'''Xoutil extensions for writing code that runs on Python 2 and 3

The name comes from (Manu's idea') "2 raised to the power of 3".

There is an existing library written by "Benjamin Peterson" named `six`_, both
(`xoutil.eight` and `six`) can be used together since this module don't claim
to be a replacement of `six`, just some extra extensions.  Nevertheless, there
are some simple definitions that even when are in `six` also are defined also
here.

This package also fixes some issues from PyPy interpreter.

.. _six: https://pypi.python.org/pypi/six

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

import sys

# Python versions

_py2 = sys.version_info[0] == 2
_py3 = sys.version_info[0] == 3
_py33 = sys.version_info >= (3, 3, 0)
_pypy = sys.version.find('PyPy') >= 0

del sys

try:
    from hashlib import sha1 as sha
except ImportError:
    from sha import sha    # noqa

try:
    base_string = basestring
    string_types = (str, unicode)
except NameError:
    base_string = str
    string_types = (str, )

if _py3:
    integer_types = int,
    class_types = type,
    text_type = str
    unichr = chr
else:
    from types import ClassType
    integer_types = (int, long)
    class_types = (type, ClassType)
    text_type = unicode
    unichr = unichr
    del ClassType

binary_type = bytes


def typeof(obj):
    '''Obtain the object's type compatible with Py 2**3.'''
    if _py3:
        return type(obj)
    else:
        from types import InstanceType as OldClass
        return obj.__class__ if isinstance(obj, OldClass) else type(obj)


try:
    __intern = intern

    def intern(string):
        # Avoid problems in Python 2.x when using unicode by default.
        return __intern(str(str() + string))

    intern.__doc__ = __intern.__doc__
except NameError:
    from sys import intern    # noqa


if _py3:
    input = input
    range = range
    zip = zip
else:
    range = xrange
    input = raw_input
    from itertools import izip as zip    # noqa


def iterkeys(d):
    '''Return an iterator over the keys of a dictionary.'''
    return (d.keys if _py3 else d.iterkeys)()


def itervalues(d):
    '''Return an iterator over the values of a dictionary.'''
    return (d.values if _py3 else d.itervalues)()


def iteritems(d):
    '''Return an iterator over the (key, value) pairs of a dictionary.'''
    return (d.items if _py3 else d.iteritems)()


try:
    callable = callable
except NameError:
    def callable(obj):
        return any('__call__' in cls.__dict__ for cls in type(obj).__mro__)


if _py3:
    from io import StringIO
else:
    from StringIO import StringIO    # noqa


if _py3:
    import builtins
    exec_ = getattr(builtins, 'exec')  # noqa
else:
    def exec_(_code_, _globs_=None, _locs_=None):
        """Execute code in a namespace."""
        import sys
        if _globs_ is None:
            frame = sys._getframe(1)
            _globs_ = frame.f_globals
            if _locs_ is None:
                _locs_ = frame.f_locals
            del frame
        elif _locs_ is None:
            _locs_ = _globs_
        exec("""exec _code_ in _globs_, _locs_""")
