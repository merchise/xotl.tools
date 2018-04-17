#!/usr/bin/env python
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

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import)

from xoutil.versions import python_version


try:
    from hashlib import sha1 as sha    # noqa
except ImportError:
    from sha import sha    # noqa

try:
    base_string = basestring
    string_types = (str, unicode)
except NameError:
    base_string = str
    string_types = (str, )

if python_version == 3:
    integer_types = int,
    long_int = int
    class_types = type,
    text_type = str
    unichr = chr
else:
    from types import ClassType
    integer_types = (int, long)
    long_int = long
    class_types = (type, ClassType)
    text_type = unicode
    unichr = unichr
    del ClassType

binary_type = bytes
UnicodeType = text_type
StringTypes = string_types

#: Define a tuple with both base types in Python 2 and containing only `type`
#: in Python 3.
ClassTypes = class_types


try:
    buffer
except NameError:
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


def typeof(obj):
    '''Obtain the object's type (compatible with Python 2**3).'''
    if _py3:
        return type(obj)
    else:
        from types import InstanceType
        return obj.__class__ if isinstance(obj, InstanceType) else type(obj)


def force_type(obj):
    '''Ensure return a valid type from `obj`.

    If `obj` is already a "type", return itself, else obtain its type.

    '''
    return obj if isinstance(obj, class_types) else typeof(obj)


def type_name(obj):
    '''Return the type name.'''
    return typeof(obj).__name__


try:
    from sys import intern
except ImportError:
    from __builtin__ import intern as __intern

    def intern(string):
        # Avoid problems in Python 2.x when using unicode
        if _py2 and isinstance(string, unicode):
            string = string.encode('utf-8')
        return __intern(string)

    # Avoid a Sphinx error
    intern.__doc__ = __intern.__doc__.replace("``", '"').replace("''", '"')


if _py3:
    input = input
    range = range
else:
    range = xrange
    input = raw_input

if _py3:    # future_builtins definitions
    ascii = ascii    # noqa
    hex, oct, filter, map, zip = hex, oct, filter, map, zip
else:
    from future_builtins import *    # noqa


def iterkeys(d):
    '''Return an iterator over the keys of a dictionary.'''
    return iter((d.keys if _py3 else d.iterkeys)())


def itervalues(d):
    '''Return an iterator over the values of a dictionary.'''
    return iter((d.values if _py3 else d.itervalues)())


def iteritems(d):
    '''Return an iterator over the (key, value) pairs of a dictionary.'''
    return iter((d.items if _py3 else d.iteritems)())


if _py3:
    from io import StringIO
else:
    from StringIO import StringIO    # noqa


try:
    import __builtin__    # noqa
    builtins = __builtin__
except ImportError:
    import builtins    # noqa
    __builtin__ = builtins


try:
    callable = getattr(__builtin__, 'callable')    # noqa
except AttributeError:
    def callable(obj):
        '''Return whether `obj` is callable (i.e., some kind of function).

        Note that classes are callable, as are instances of classes with a
        __call__() method.

        '''
        return any('__call__' in cls.__dict__ for cls in type(obj).__mro__)


try:
    exec_ = getattr(builtins, 'exec')    # noqa
except AttributeError:
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


try:
    execfile = getattr(__builtin__, 'execfile')  # noqa
except AttributeError:
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
