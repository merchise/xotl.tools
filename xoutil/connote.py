# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.connote
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created 2015-07-11

'''A *predicate* is seen as a property that a subject has or is characterized
by.  A predicate is therefore an expression that can be true of something
(involve as a necessary condition of consequence).  Thus, the expression "is
moving" is true of those things that are moving.

The main class of this module is :class:`Predicate`.

.. versionadded:: 1.7.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)


from xoutil.functools import lwraps as lw


class Predicate(object):
    '''A definition of a validation function using a grammar of simple
    predicates.

    All parameters are checkers; those given by name (keyword arguments) are
    used to produce named anonymous checkers, for example:

      >>> from xoutil.predicate import Predicate
      >>> p = Predicate(int, is_valid_age=lambda age: 0 < age <= 120)

    A lambda wrapper (:func:`lw`) can be used to decorate anonymous functions;
    so, last declaration is equivalent to::

      >>> p = Predicate(int, lw('is_valid_age', lambda age: 0 < age <= 120))

    There is a special keyword argument ('__named__'); if present and True; a
    name will be generated for the predicate.

    Each checker could be:

    - A type (or tuple of types) to test with ``isinstance(value, checker)``

    - A set, a value will be valid if is contained in the set.

    - A mapping, a value will be valid if is contained in the mapping and its
      value is True.

    - A tuple of other inner checkers, if any of the checkers validates a
      value, the value is valid (OR).

    - A list of other inner checkers, all checkers must validate the value
      (AND).

    - A callable that receives the value and returns True if the value is
      valid.

    - ``True``, ``False`` or any instance of `Logical` could be used as
      checkers always validating or invalidating the value.

    - An empty list is synonym of ``True``, an empty tuple, set or mapping is
      synonym of ``False``.

    Any other value will return False (fail).

    .. note:: Above definition is controversial, maybe a exception must be
              raised if a invalid checker is used.

    With this class, it could be built real type checkers, for example::

      >>> from xoutil.predicate import Predicate as pp
      >>> numbers = (int, float)
      >>> is_valid_age = pp(numbers, valid_age=lambda age: 0 < age <= 120)
      >>> is_valid_age(100)
      True

      >>> is_valid_age(130)
      False

      >>> is_valid_age(85.5)
      True

    Other simple example::

      >>> always_true = predicate(True)
      >>> always_true(False)
      True

      >>> always_false = predicate(False)
      >>> always_false(True)
      False

      >>> always_true = predicate()
      >>> always_true(1)
      True

      >>> always_true('any string')
      True

      >>> always_false = predicate(())
      >>> always_false(1)
      False

      >>> always_false('any string')
      False

    '''
    __slots__ = ('__name__', 'checkers', 'failed_stack')
    DEFAULT_NAME = str('predicate')

    def __init__(self, *args, **kwargs):
        '''Create a predicate.'''
        named = kwargs.pop('__named__', False)
        self.checkers = list(args)
        for name in kwargs:
            self.checkers.append(lw(name, kwargs[name]))
        self.failed_stack = []
        self.__name__ = self.DEFAULT_NAME
        if named:
            self.get_name()

    def get_name(self):
        '''Get a name representation suitable for this predicate.

        This method is used in the constructor to cache this value if keyword
        argument '__named__' is given and True.

        '''
        if self.__name__ == self.DEFAULT_NAME:
            self.__name__ = _get_checker_name(self.checkers)
        return self.__name__

    __str__ = get_name

    def __repr__(self):
        return _get_checker_name(self.checkers, full=True)

    def __call__(self, obj):
        '''Check is `obj` is a valid instance for a set of checkers.'''
        from xoutil.logical import Logical
        from xoutil.collections import Set, Mapping
        from xoutil.eight import callable

        def valid(chk, stack=True):
            if isinstance(chk, (bool, Logical)):
                res = bool(chk)
            elif isinstance(chk, type):
                res = isinstance(obj, chk)
            elif isinstance(chk, tuple):
                if not chk:
                    res = False
                elif all(isinstance(c, type) for c in chk):
                    res = isinstance(obj, chk)
                else:
                    res = any(valid(c, stack=False) for c in chk)
            elif isinstance(chk, list):
                res = all(valid(c) for c in chk)
            elif isinstance(chk, Set):
                res = obj in chk
            elif isinstance(chk, Mapping):
                res = chk.get(obj, False)
            elif callable(chk):
                res = chk(obj)
            else:
                res = False
            if not res and stack:
                self.failed_stack.append(chk)
            return res

        self.failed_stack = []
        aux = (chk for chk in self.checkers if not valid(chk))
        return next(aux, None) is None


def _get_checker_name(checker, full=False):
    '''Return a nice name for a `checker`.

    :param full: If True, return a detailed representation of the checker.

    See :class:`Predicate` for possible checker kinds.

    '''
    from xoutil.logical import Logical
    from xoutil.collections import Set, Mapping, PascalSet
    from xoutil.eight import callable
    from xoutil.inspect import type_name
    from xoutil.string import safe_str as sstr    # , safe_repr as srepr
    srepr = repr
    if isinstance(checker, (bool, Logical)):
        return str(checker)
    elif isinstance(checker, Predicate):
        return str('p(%s)') % checker.get_name()
    elif isinstance(checker, type):
        return type_name(checker, affirm=True)
    elif isinstance(checker, list):
        if not checker:
            return str(True)
        else:
            return str(' & ').join(_get_checker_name(c) for c in checker)
    elif isinstance(checker, tuple):
        if not checker:
            return str(False)
        elif all(isinstance(c, type) for c in checker):
            return type_name(checker, affirm=True)
        else:
            res = str(' | ').join(_get_checker_name(c) for c in checker)
            return str('(%s)' % res)
    elif isinstance(checker, PascalSet):
        return str(checker)
    elif isinstance(checker, Set):
        if checker:
            aux = srepr(next(iter(checker)))
            if len(checker) > 1:
                aux += str(', ...')
        else:
            aux = str()
        return str('{%s}') % aux
    elif isinstance(checker, Mapping):
        if checker:
            key = next(iter(checker))
            aux = str('%s: %s') % (srepr(key), srepr(checker[key]))
            if len(checker) > 1:
                aux += str(', ...')
        else:
            aux = str()
        return str('{%s}') % aux
    elif callable(checker):
        res = type_name(checker, affirm=True)
        if 'lambda' in res:
            from inspect import getargspec
            res = res.replace('<lambda>', '<λ>')
            args = getargspec(checker).args
            res = sstr('%s(%s)' % (res, ', '.join(args)))
        return res
    else:
        return str('False(%)' % srepr(checker))
