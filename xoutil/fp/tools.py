#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.fp.tools
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-10-05

'''Tools for working with functions in a more "pure" way.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.eight.meta import metaclass
from xoutil.eight.abc import ABCMeta


def identity(arg):
    '''Returns its argument unaltered.'''
    return arg


class MetaCompose(ABCMeta):
    '''Meta-class for function composition.'''
    def __instancecheck__(self, instance):
        '''Override for ``isinstance(instance, self)``.'''
        from xoutil.eight import callable
        res = super(MetaCompose, self).__instancecheck__(instance)
        if not res:
            # TODO: maybe only those with parameters.
            res = callable(instance)
        return res

    def __subclasscheck__(self, subclass):
        '''Override for ``issubclass(subclass, self)``.'''
        res = super(MetaCompose, self).__subclasscheck__(subclass)
        if not res:
            import types as t
            res = subclass in {t.FunctionType, t.MethodType, t.LambdaType,
                               t.BuiltinFunctionType, t.BuiltinMethodType}
        return res


class compose(metaclass(MetaCompose)):
    '''Composition of several functions.

    Functions are composed right to left.  A composition of zero functions
    gives back the `identity`:func: function.

    Rules must be fulfilled (those inner `all`)::

      >>> x = 15
      >>> f, g, h = x.__add__, x.__mul__, x.__xor__
      >>> all((compose() is identity,
      ...      # identity functions are optimized
      ...      compose(identity, identity) is identity,
      ...      compose()(x) is x,
      ...      compose(f) is f,
      ...      compose(g, f)(x) == g(f(x)),
      ...      compose(h, g, f)(x) == h(g(f(x)))))
      True

    '''
    __slots__ = ('inner', 'scope')

    def __new__(cls, *functions):
        functions = [fn for fn in functions if fn is not identity]
        count = len(functions)
        if count == 0:
            return identity
        elif count == 1:
            return functions[0]
        else:
            from xoutil import Unset
            self = super(compose, cls).__new__(cls)
            self.inner = functions
            self.scope = Unset
            return self

    def __call__(self, *args, **kwds):
        funcs = self.inner
        count = len(funcs)
        if count:
            i = 1
            while i <= count:
                try:
                    fn = funcs[-i]
                    if i == 1:
                        res = fn(*args, **kwds)
                    else:
                        res = fn(res)
                except BaseException:
                    self.scope = (count - i, fn)
                    raise
                i += 1
            return res
        else:
            return identity(*args, **kwds)

    def __repr__(self):
        '''Get composed function representation'''
        from xoutil.tools import nameof
        if self.inner:
            def getname(fn):
                return nameof(fn).replace((lambda: None).__name__, 'λ')
            return ' . '.join(getname(fn) for fn in self.inner)
        else:
            return nameof(identity)

    def __str__(self):
        '''Get composed function string'''
        count = len(self.inner)
        if count == 0:
            return identity.__doc__
        else:
            res = self.inner[0].__doc__ if count == 1 else None
            if not res:
                res = 'Composed function: <{!r}>'.format(self)
            return res

    __name__ = property(__repr__)
    __doc__ = property(__str__)

    def __eq__(self, other):
        if isinstance(type(other), MetaCompose):
            return self.inner == other.inner
        elif self.inner:
            return self.inner[0] == other
        else:
            return other is identity

    def __len__(self):
        return len(self.inner)

    def __iter__(self):
        return iter(self.inner)

    def __contains__(self, item):
        return item in self.inner

    def __getitem__(self, index):
        res = self.inner[index]
        return compose(*res) if isinstance(res, list) else res

    def __setitem__(self, index, value):
        if isinstance(index, slice) and isinstance(type(value), MetaCompose):
            value = value.inner
        self.inner[index] = value

    def __delitem__(self, index):
        del self.inner[index]
