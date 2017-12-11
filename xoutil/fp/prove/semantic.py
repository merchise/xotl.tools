#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Prove validity of values - Base predicate classes.

A `predicate`:class: could combine two concepts (*validation* and
*conversion*) in a single callable object.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


class predicate(object):
    '''Base class for value proves using logic predicates.

    A predicate could combine two operations on values: *validation*, and
    *conversion*.

    To signal that value as invalid, a predicate must return the special value
    `_wrong`.  Types work as in `isinstance`:func: standard function; callable
    functions mould a parameter value into a definitive form.

    To use normal functions as a callable predicate, use `SafeCheck`:class: or
    `LogicalCheck`:class` to wrap them.

    When using a list to combine explicitly the two concepts, result of the
    check part is considered Boolean (True or False), and the second part
    alwasy return a moulded value.

    When use a predicate, several definitions will be tried until one succeed.

    '''
    __slots__ = ('inner',)

    def __new__(cls, *args):
        from xoutil.eight import class_types, callable, type_name
        if cls is predicate:    # Parse the right sub-type
            count = len(args)
            if count == 0:
                msg = '{}() takes at least 1 argument (0 given)'
                raise TypeError(msg.format(cls.__name__))
            elif count == 1:
                arg = args[0]
                if isinstance(arg, cls):
                    return arg
                elif isinstance(arg, class_types + (tuple,)):
                    return TypeCheck(arg)
                elif isinstance(arg, list):
                    return CheckAndCast(*arg)
                elif callable(arg):
                    return LogicalCheck(arg)
                else:
                    msg = "{}() can't parse a definition of type: {}"
                    raise TypeError(msg.format(cls.__name__, type_name(arg)))
            else:
                return MultiCheck(*args)
        else:
            return super(predicate, cls).__new__(cls)

    def __init__(self, *args):
        pass

    def __repr__(self):
        return str(self)


class TypeCheck(predicate):
    '''Check if value is instance of given types.'''
    __slots__ = ()

    def __new__(cls, *args):
        from xoutil.eight import class_types as _types, type_name
        from xoutil.params import check_count
        check_count(len(args) + 1, 2, caller=cls.__name__)
        if len(args) == 1 and isinstance(args[0], tuple):
            args = args[0]
        if all(isinstance(arg, _types) for arg in args):
            self = super(TypeCheck, cls).__new__(cls)
            self.inner = args
            return self
        else:
            wrong = (arg for arg in args if not isinstance(arg, _types))
            wnames = ', or '.join(type_name(w) for w in wrong)
            msg = '`TypeCheck` allows only valid types, not: ({})'
            raise TypeError(msg.format(wnames))

    def __call__(self, value):
        from xoutil.fp.option import Just, Wrong
        ok = isinstance(value, self.inner)
        return (value if value else Just(value)) if ok else Wrong(value)

    def __str__(self):
        return self._str()

    def __crop__(self, max_width=None, canonical=False):
        '''Calculate both string versions (small and normal).'''
        from xoutil.symbols import Undefined
        from xoutil.eight import type_name
        from xoutil.clipping import ELLIPSIS, DEFAULT_MAX_WIDTH
        if max_width is None:
            max_width = DEFAULT_MAX_WIDTH    # a big number for this
        start, end = '{}('.format(type_name(self)), ')'
        borders_len = len(start) + len(end)
        sep = ', '
        res = ''
        items = iter(self.inner)
        ok = True
        while ok:
            item = next(items, Undefined)
            if item is not Undefined:
                if res:
                    res += sep
                aux = item.__name__
                if len(res) + len(aux) + borders_len <= max_width:
                    res += aux
                else:
                    res += ELLIPSIS
                    ok = False
            else:
                ok = False
        return '{}{}{}'.format(start, res, end)


class NoneOrTypeCheck(TypeCheck):
    '''Check if value is None or instance of given types.'''
    __slots__ = ()

    def __call__(self, value):
        from xoutil.fp.option import Wrong
        if value is None:
            _types = self.inner
            i, res = 0, None
            while res is None and i < len(_types):
                try:
                    res = _types[i]()
                except Exception:
                    pass
                i += 1
            return res if res is not None else Wrong(None)
        else:
            return super(NoneOrTypeCheck, self).__call__(value)

    def __str__(self):
        aux = super(NoneOrTypeCheck, self).__str__()
        return 'none-or-{}'.format(aux)


class TypeCast(TypeCheck):
    '''Cast a value to a correct type.'''
    __slots__ = ()

    def __call__(self, value):
        from xoutil.fp.option import Just
        res = super(TypeCast, self).__call__(value)
        if not res:
            _types = self.inner
            i = 0
            while not res and i < len(_types):
                try:
                    res = _types[i](value)
                    if not res:
                        res = Just(res)
                except Exception:
                    pass
                i += 1
        return res

    def __str__(self):
        # FIX: change this
        aux = super(NoneOrTypeCheck, self).__str__()
        return 'none-or-{}'.format(aux)


class CheckAndCast(predicate):
    '''Check if value, if valid cast it.

    Result value must be valid also.
    '''
    __slots__ = ()

    def __new__(cls, check, cast):
        from xoutil.eight import callable, type_name
        check = predicate(check)
        if callable(cast):
            self = super(CheckAndCast, cls).__new__(cls)
            self.inner = (check, SafeCheck(cast))
            return self
        else:
            msg = '{}() expects a callable for cast, "{}" given'
            raise TypeError(msg.format(type_name(self), type_name(cast)))

    def __call__(self, value):
        from xoutil.fp.option import Wrong
        check, cast = self.inner
        aux = check(value)
        if aux:
            res = cast(value)
            if check(res):
                return res
        else:
            res = aux
        if isinstance(res, Wrong):
            return res
        else:
            return Wrong(value)

    def __str__(self):
        from xoutil.clipping import crop
        check, cast = self.inner
        fmt = '({}(…) if {}(…) else _wrong)'
        return fmt.format(crop(cast), check)


class FunctionalCheck(predicate):
    '''Check if value is valid with a callable function.'''
    __slots__ = ()

    def __new__(cls, check):
        from xoutil.eight import callable, type_name
        # TODO: Change next, don't use isinstance
        if isinstance(check, predicate):
            return check
        elif callable(check):
            self = super(FunctionalCheck, cls).__new__(cls)
            self.inner = check
            return self
        else:
            msg = 'a functional check expects a callable but "{}" is given'
            raise TypeError(msg.format(type_name(check)))

    def __str__(self):
        from xoutil.eight import type_name
        from xoutil.clipping import crop
        suffix = 'check'
        kind = type_name(self).lower()
        if kind.endswith(suffix):
            kind = kind[:-len(suffix)]
        inner = crop(self.inner)
        return '{}({})()'.format(kind, inner)


class LogicalCheck(FunctionalCheck):
    '''Check if value is valid with a callable function.'''
    __slots__ = ()

    def __call__(self, value):
        from xoutil.fp.option import Just, Wrong
        try:
            res = self.inner(value)
            if res:
                if isinstance(res, Just):
                    return res
                elif res is True:
                    return Just(value)
                else:
                    return res
            elif isinstance(res, Wrong):
                return res
            elif res is False or res is None:    # XXX: None?
                return Wrong(value)
            else:
                return Wrong(res)
        except Exception as error:
            return Wrong(error)


class SafeCheck(FunctionalCheck):
    '''Return a wrong value only if function produce an exception.'''
    __slots__ = ()

    def __call__(self, value):
        from xoutil.fp.option import Wrong
        try:
            return self.inner(value)
        except Exception as error:
            return Wrong(error)


class MultiCheck(predicate):
    '''Return a wrong value only when all inner predicates fails.

    Haskell: guards (pp. 132)

    '''
    __slots__ = ()

    def __new__(cls, *args):
        inner = tuple(predicate(arg) for arg in args)
        self = super(MultiCheck, cls).__new__(cls)
        self.inner = inner
        return self

    def __call__(self, value):
        from xoutil.fp.option import Just, Wrong, none
        predicates = self.inner
        i, res = 0, none
        while isinstance(res, Wrong) and i < len(predicates):
            res = predicates[i](value)
            i += 1
        return res.inner if isinstance(res, Just) and res.inner else res

    def __str__(self):
        aux = ' OR '.join(str(c) for c in self.inner)
        return 'combo({})'.format(aux)
