# Back-ported from Python 3.2.
# Copyright (c) 2001-2012, 2014, 2015, 2016, Python Software Foundation; All rights reserved.
# Retains the licence of the Python Software Foundation.

"""Redo the builtin repr() (representation) but with limits on most sizes."""


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

# TODO: Must be moved to `eight` and remove `unicode_literals` import
import sys

if sys.version_info >= (3, 2, 0):
    from reprlib import Repr, repr, recursive_repr, __all__
else:
    # Don't use name list here to avoid module recursive use
    __all__ = (str("Repr"), str("repr"), str("recursive_repr"))

    if sys.version_info <= (3, 1, 0):
        import __builtin__ as builtins
    else:
        import builtins
    from itertools import islice
    if sys.version_info >= (3, 0):
        try:
            from _thread import get_ident
        except ImportError:
            from _dummy_thread import get_ident
    else:
        try:
            from thread import get_ident
        except ImportError:
            from dummy_thread import get_ident

    def recursive_repr(fillvalue='...'):
        '''Decorator to make a repr function return ``fillvalue`` for a recursive
        call'''

        def decorating_function(user_function):
            repr_running = set()

            def wrapper(self):
                key = id(self), get_ident()
                if key in repr_running:
                    return fillvalue
                repr_running.add(key)
                try:
                    result = user_function(self)
                finally:
                    repr_running.discard(key)
                return result

            # Can't use functools.wraps() here because of bootstrap issues
            wrapper.__module__ = getattr(user_function, '__module__')
            wrapper.__doc__ = getattr(user_function, '__doc__')
            wrapper.__name__ = getattr(user_function, '__name__')
            wrapper.__annotations__ = getattr(user_function,
                                              '__annotations__', {})
            return wrapper

        return decorating_function

    class Repr(object):

        def __init__(self):
            self.maxlevel = 6
            self.maxtuple = 6
            self.maxlist = 6
            self.maxarray = 5
            self.maxdict = 4
            self.maxset = 6
            self.maxfrozenset = 6
            self.maxdeque = 6
            self.maxstring = 30
            self.maxlong = 40
            self.maxother = 30

        def repr(self, x):
            return self.repr1(x, self.maxlevel)

        def repr1(self, x, level):
            from xoutil.eight import type_name
            typename = type_name(x)
            if ' ' in typename:
                parts = typename.split()
                typename = '_'.join(parts)
            if hasattr(self, 'repr_' + typename):
                return getattr(self, 'repr_' + typename)(x, level)
            else:
                return self.repr_instance(x, level)

        def _repr_iterable(self, x, level, left, right, maxiter, trail=''):
            n = len(x)
            if level <= 0 and n:
                s = '...'
            else:
                newlevel = level - 1
                repr1 = self.repr1
                pieces = [repr1(elem, newlevel) for elem in islice(x, maxiter)]
                if n > maxiter:
                    pieces.append('...')
                s = ', '.join(pieces)
                if n == 1 and trail:
                    right = trail + right
            return '%s%s%s' % (left, s, right)

        def repr_tuple(self, x, level):
            return self._repr_iterable(x, level, '(', ')', self.maxtuple, ',')

        def repr_list(self, x, level):
            return self._repr_iterable(x, level, '[', ']', self.maxlist)

        def repr_array(self, x, level):
            header = "array('%s', [" % x.typecode
            return self._repr_iterable(x, level, header, '])', self.maxarray)

        def repr_set(self, x, level):
            x = _possibly_sorted(x)
            return self._repr_iterable(x, level, 'set([', '])', self.maxset)

        def repr_frozenset(self, x, level):
            x = _possibly_sorted(x)
            return self._repr_iterable(x, level, 'frozenset([', '])',
                                       self.maxfrozenset)

        def repr_deque(self, x, level):
            return self._repr_iterable(x, level, 'deque([', '])',
                                       self.maxdeque)

        def repr_dict(self, x, level):
            n = len(x)
            if n == 0:
                return '{}'
            if level <= 0:
                return '{...}'
            newlevel = level - 1
            repr1 = self.repr1
            pieces = []
            for key in islice(_possibly_sorted(x), self.maxdict):
                keyrepr = repr1(key, newlevel)
                valrepr = repr1(x[key], newlevel)
                pieces.append('%s: %s' % (keyrepr, valrepr))
            if n > self.maxdict:
                pieces.append('...')
            s = ', '.join(pieces)
            return '{%s}' % (s,)

        def repr_str(self, x, level):
            s = builtins.repr(x[:self.maxstring])
            if len(s) > self.maxstring:
                i = max(0, (self.maxstring-3)//2)
                j = max(0, self.maxstring-3-i)
                s = builtins.repr(x[:i] + x[len(x)-j:])
                s = s[:i] + '...' + s[len(s)-j:]
            return s

        def repr_int(self, x, level):
            s = builtins.repr(x)  # XXX Hope this isn't too slow...
            if len(s) > self.maxlong:
                i = max(0, (self.maxlong-3)//2)
                j = max(0, self.maxlong-3-i)
                s = s[:i] + '...' + s[len(s)-j:]
            return s

        def repr_instance(self, x, level):
            try:
                s = builtins.repr(x)
                # Bugs in x.__repr__() can cause arbitrary
                # exceptions -- then make up something
            except Exception:
                return '<%s instance at %x>' % (x.__class__.__name__, id(x))
            if len(s) > self.maxother:
                i = max(0, (self.maxother-3)//2)
                j = max(0, self.maxother-3-i)
                s = s[:i] + '...' + s[len(s)-j:]
            return s

    def _possibly_sorted(x):
        # Since not all sequences of items can be sorted and comparison
        # functions may raise arbitrary exceptions, return an unsorted
        # sequence in that case.
        try:
            return sorted(x)
        except Exception:
            return list(x)

    aRepr = Repr()
    repr = aRepr.repr
