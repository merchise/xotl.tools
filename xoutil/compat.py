# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.compat
#----------------------------------------------------------------------
#
# ============================ Original copyright notice ===================
# Copyright (C) 2005-2011, 2014 the SQLAlchemy authors and contributors
#
# This module is based on part of SQLAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
# ============================ Original copyright notice ===================

"""Handle Python version/platform incompatibilities."""

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

import warnings
warnings.warn('The xoutil.compat module is being deprecated in favor of '
              'xoutil.six')
import sys

# TODO: Changes in Python 3
#    * remove "iteritems", "itervalues", "iterkeys" for dict
#    * basestring, str, unicode
#    * "__builtin__" is now "builtins"
#    * "import cPickle as pickle" not needed any more
#    * __metaclass__
#    * "m.im_class" is "m.__self__.__class__"
#    * many "types.*" are removed: types.ClassType = type
#    * "StandardError" removed
#    * xrange
#    * "long" integrated with "int"
#    * The StringIO and cStringIO modules are gone. Instead, import the io
#      module and use io.StringIO or io.BytesIO for text and data respectively.
#    * "exec" is a function
#    * Integer literals no longer support a trailing l or L.
#    * String literals no longer support a leading u or U.
#    * Classic classes are gone
#    * except type, var is not longer supported
#    * "__nonzero__" -> "__bool__"

# TODO: Make compatible all libraries and applications with Python 2.7

try:
    import threading
except ImportError:
    import dummy_threading as threading

py32 = sys.version_info >= (3, 2)
py33 = sys.version_info >= (3, 3)
py3k = getattr(sys, 'py3kwarning', False) or sys.version_info >= (3, 0)
jython = sys.platform.startswith('java')
pypy = hasattr(sys, 'pypy_version_info')
win32 = sys.platform.startswith('win')

if py3k:
    import builtins
    str_base = str
    str_types = (str, )
    u = _unicode = str
    ext_str_types = (bytes, str)
    TypeType = type
    class_types = (type, )
    integer = long = int
    integers = (int, )
    # TODO: [manu] Remove all "xrange" and all aliases:
    #       "xoutil.compat.range" will be "xrange" in Python 2.x and will
    #       remains unchanged in Python 2.0
    from builtins import range as xrange
    xrange_ = xrange
    range_ = range = lambda *args: list(xrange(*args))
    exec_ = getattr(builtins, "exec")
    def execfile_(fname, *args):
        return exec_(compile(open(fname, 'rb').read(), fname, 'exec'), *args)
else:
    str_base = basestring
    str_types = (str, unicode)
    _unicode = unicode
    ext_str_types = (str, unicode)
    from types import TypeType
    class_types = (type, TypeType)
    # FIXME: [manu] In Py2  isinstance(1, long) is False.
    integers = (long, int)
    integer = long
    from __builtin__ import xrange, range, execfile
    xrange_ = xrange
    range_ = range
    execfile_ = execfile

    def exec_(code, globs=None, locs=None):
        """Execute code in a namespace."""
        if globs is None:
            frame = sys._getframe(1)
            globs = frame.f_globals
            if locs is None:
                locs = frame.f_locals
            del frame
        elif locs is None:
            locs = globs
        exec("""exec code in globs, locs""")


if py3k:
    set_types = set
elif sys.version_info < (2, 6):
    import sets
    set_types = set, sets.Set
else:
    # 2.6 deprecates sets.Set, but we still need to be able to detect them
    # in user code and as return values from DB-APIs
    ignore = ('ignore', None, DeprecationWarning, None, 0)
    import warnings
    try:
        warnings.filters.insert(0, ignore)
    except Exception:
        import sets
    else:
        import sets
        warnings.filters.remove(ignore)
    set_types = set, sets.Set

if py3k:
    import pickle
else:
    try:
        import cPickle as pickle
    except ImportError:
        import pickle


if py3k:
    import configparser
else:
    import ConfigParser as configparser
    ConfigParser = configparser


if py3k:
    from inspect import getfullargspec as inspect_getfullargspec
else:
    from inspect import getargspec as inspect_getfullargspec


if py3k and not py32:
    def callable(obj):
        '''callable(object) -> bool

        Return whether the object is callable (i.e., some kind of function).
        Note that classes are callable, as are instances of classes with a
        __call__() method.

        '''
        return hasattr(obj, '__call__')
else:
    # Removed in Python 3 and brought back in 3.2.  brilliant!
    try:
        from builtins import callable
    except ImportError:
        from __builtin__ import callable


if py3k:
    def cmp(a, b):
        return (a > b) - (a < b)

    # Remove this import, always use it directly
    from functools import reduce
else:
    from __builtin__ import cmp, reduce

try:
    from collections import defaultdict
except ImportError:
    class defaultdict(dict):
        def __init__(self, default_factory=None, *a, **kw):
            if (default_factory is not None and
                not hasattr(default_factory, '__call__')):
                raise TypeError('first argument must be callable')
            dict.__init__(self, *a, **kw)
            self.default_factory = default_factory
        def __getitem__(self, key):
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                return self.__missing__(key)
        def __missing__(self, key):
            if self.default_factory is None:
                raise KeyError(key)
            self[key] = value = self.default_factory()
            return value
        def __reduce__(self):
            if self.default_factory is None:
                args = tuple()
            else:
                args = self.default_factory,
            return type(self), args, None, None, self.iteritems()
        def copy(self):
            return self.__copy__()
        def __copy__(self):
            return type(self)(self.default_factory, self)
        def __deepcopy__(self, memo):
            import copy
            return type(self)(self.default_factory,
                              copy.deepcopy(self.items()))
        def __repr__(self):
            return 'defaultdict(%s, %s)' % (self.default_factory,
                                            dict.__repr__(self))


# find or create a dict implementation that supports __missing__
class _probe(dict):
    def __missing__(self, key):
        return 1

try:
    _probe()['missing']
    py25_dict = dict
except KeyError:
    class py25_dict(dict):
        def __getitem__(self, key):
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                try:
                    missing = self.__missing__
                except AttributeError:
                    raise KeyError(key)
                else:
                    return missing(key)
finally:
    del _probe


try:
    import hashlib
    _md5 = hashlib.md5
except ImportError:
    import md5
    _md5 = md5.new


def md5_hex(x):
    # Py3K
    #x = x.encode('utf-8')
    m = _md5()
    m.update(x)
    return m.hexdigest()

import time
if win32 or jython:
    time_func = time.clock
else:
    time_func = time.time

if sys.version_info >= (2, 5):
    def decode_slice(slc):
        """decode a slice object as sent to __getitem__.

        takes into account the 2.5 __index__() method, basically.

        """
        ret = []
        for x in slc.start, slc.stop, slc.step:
            if hasattr(x, '__index__'):
                x = x.__index__()
            ret.append(x)
        return tuple(ret)
else:
    def decode_slice(slc):
        return (slc.start, slc.stop, slc.step)

if sys.version_info >= (2, 6):
    from operator import attrgetter as dottedgetter
else:
    def dottedgetter(attr):
        def g(obj):
            for name in attr.split("."):
                obj = getattr(obj, name)
            return obj
        return g

import decimal  # TODO: Why 'decimal' is here?


if py3k:    # pragma: no cover
    def iteritems_(d):
        return d.items()
    def itervalues_(d):
        return d.values()
    def iterkeys_(d):
        return d.keys()
else:
    def iteritems_(d):
        return d.iteritems()
    def itervalues_(d):
        return d.itervalues()
    def iterkeys_(d):
        return d.iterkeys()

try:
    import ConfigParser as configparser
except:
    import configparser     # Name changed in Python3

try:
    from future_builtins import zip
except ImportError:
    from builtins import zip
izip = zip

try:
    from future_builtins import map
except ImportError:
    from builtins import map
imap = map

try:
    from itertools import izip_longest as zip_longest
except ImportError:
    from itertools import zip_longest
izip_longest = zip_longest


if py3k:
    from builtins import chr
else:
    from __builtin__ import unichr as chr


if py3k:
    from builtins import input
else:
    from __builtin__ import raw_input as input
