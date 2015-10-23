#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.values
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-07-15

'''Some generic coercers (or checkers) for value types.

This module coercion function are not related in any way to deprecated old
python feature, are similar to a combination of object mold/check:

- *Mold* - Fit values to expected conventions.

- *Check* - These functions must return `Invalid`\ [#pyni]_ special value to
  specify that expected fit is not possible.

.. [#pyni] We don't use Python classic `NotImplemented` special value in order
           to obtain False if the value is not coerced (`Invalid`).

A custom coercer could be created with closures, for an example see
`create_int_range_coerce`:func:.

Also contains sub-modules to obtain, convert and check values of common types.

.. versionadded:: 1.7.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


import sys
from re import compile as regex_compile
from xoutil.eight.abc import ABCMeta
from xoutil.eight.meta import metaclass
from xoutil.functools import lwraps
from xoutil.logical import Logical as InvalidType


Invalid = InvalidType('Invalid')


_coercer_decorator = lwraps(__coercer__=True)


def valid(arg):
    '''True if `arg` is not Invalid.'''
    return arg is not Invalid


def check(coerce, arg):
    '''Coerce `arg`; if invalid raises a TypeError.

    See `compose`:class: and `some`:class: on how to combine "AND" and "OR"
    coercers.

    See `create_int_range_coerce`:func: for an example.

    '''
    res = coerce(arg)
    if valid(res):
        return res
    else:
        msg = 'Value "{}" is not coerced by "{}".'
        raise TypeError(msg.format(arg, coercer_name(arg)))


class MetaCoercer(ABCMeta):
    '''Meta-class for `coercer`:class:.

    This meta-class allows that several objects are considered valid instances
    of `coercer`:class:\ :

    - Functions decorated with `coercer`:class: (used with its decorator
      facet).

    - Instances of any sub-class of `custom`:class:.

    - Instances of `coercer`:class: itself.

    See the class declaration (`coercer`:class:) for more information.

    '''
    def __instancecheck__(self, instance):
        return (getattr(instance, '__coercer__', False) or
                super(MetaCoercer, self).__instancecheck__(instance))


class coercer(metaclass(MetaCoercer)):
    '''Special coercer class.

    This class has several facets:

    - Pure type-checkers when a type or tuple of types are received as
      argument.  See `istype`:class: for more information.

    - Return equivalent coercer from some special values:

      * None -> identity_coerce

      * () -> void_coerce

    - A decorator for functions; when a function is given, decorate it to
      become a coercer.  The mark itself is not enough, functions intended to
      be coercers must fulfills the protocol (not to produce exception and
      return `Invalid` on fails).  For example::

        >>> @coercer
        ... def age_coerce(arg):
        ...     res = int_coerce(arg)
        ...     return res if valid(res) and 0 < arg <= 120 else Invalid

        >>> isinstance(age_coerce, coercer)
        True

    '''
    __slots__ = ()

    def __new__(cls, source):
        from types import FunctionType as function
        if source is None:
            return identity_coerce
        elif source is ():
            return void_coerce
        elif isinstance(source, coercer):
            return source
        elif isinstance(source, (function, staticmethod, classmethod)):
            return _coercer_decorator(source)
        else:
            inner = types_tuple_coerce(source)
            return istype(inner) if inner else Invalid


def coercer_name(arg, join=None):
    '''Get the name of a coercer.

    :param arg: Coercer to get the name.  Also processes collections (tuple,
           list or set) of coercers.  Any other value is considered invalid
           and raises an exception.

    :param join: When a collection is used; if this argument is None a
           collection of names is returned, if not None then is used to join
           the items in a resulting string.  For example::

             >>> coercer_name((int_coerce, float_coerce))
             ('int', 'float')

             >>> coercer_name((int_coerce, float_coerce), '_')
             'int_float'

           To obtain pretty-print tuples, use something like::

             >>> coercer_name((int_coerce, float_coerce),
             ...              join=lambda arg: '(%s)' % ', '.join(arg))

    This function not only works with coercers, all objects that fulfill
    needed protocol to get names will also be valid.

    '''
    # TODO: Maybe this function must be moved to `xoutil.names`
    from xoutil.eight import string_types
    if isinstance(arg, (tuple, list, set)):
        res = type(arg)(coercer_name(c) for c in arg)
        if isinstance(join, string_types):
            join = join.join
        return str(join(res)) if join else res
    else:
        try:
            res = arg.__name__
        except BaseException:
            res = str(arg)
        suffix = str('_coerce')
        if res.endswith(suffix):
            res = res[:-len(suffix)]
        return res


@coercer
def identity_coerce(arg):
    'Leaves unchanged the passed argument `arg`.'
    return arg


@coercer
def void_coerce(arg):
    '''Always `Invalid`.'''
    return Invalid


@coercer
def type_coerce(arg):
    '''Check if `arg` is a valid type.'''
    from xoutil.eight import class_types
    return arg if isinstance(arg, class_types) else Invalid


@coercer
def types_tuple_coerce(arg):
    '''Check if `arg` is valid for `isinstance` or `issubclass` 2nd argument.

    Type checkers are any class, a type or tuple of types.  For example::

      >>> types_tuple_coerce(object) == (object,)
      True

      >>> types_tuple_coerce((int, float)) == (int, float)
      true

      >>> types_tuple_coerce('not-a-type') is Invalid
      True

    See `type_coerce` for more information.

    '''
    if valid(type_coerce(arg)):
        return (arg, )
    elif isinstance(arg, tuple) and all(valid(type_coerce(t)) for t in arg):
        return arg
    else:
        return Invalid


@coercer
def callable_coerce(arg):
    '''Check if `arg` is a callable object.'''
    from xoutil.eight import callable
    return arg if callable(arg) else Invalid


@coercer
def file_coerce(arg):
    '''Check if `arg` is a file-like object.'''
    from xoutil.eight.io import is_file_like
    return arg if is_file_like(arg) else Invalid


@coercer
def float_coerce(arg):
    '''Check if `arg` is a valid float.

    Other types are checked (string, int, complex).

    '''
    from xoutil.eight import integer_types, string_types
    if isinstance(arg, float):
        return arg
    elif isinstance(arg, integer_types):
        return float(arg)
    elif isinstance(arg, string_types):
        try:
            return float(arg)
        except ValueError:
            return Invalid
    elif isinstance(arg, complex):
        return arg.real if arg.imag == 0 else Invalid
    else:
        return Invalid


@coercer
def int_coerce(arg):
    '''Check if `arg` is a valid integer.

    Other types are checked (string, float, complex).

    '''
    from xoutil.eight import integer_types
    if isinstance(arg, integer_types):
        return arg
    else:
        arg = float_coerce(arg)
        if valid(arg):
            res = int(arg)
            return res if arg - res == 0 else Invalid
        else:
            return Invalid


@coercer
def number_coerce(arg):
    '''Check if `arg` is a valid number (integer or float).

    Types that are checked (string, int, float, complex).

    '''
    from xoutil.eight import integer_types
    if isinstance(arg, integer_types):
        return arg
    else:
        f = float_coerce(arg)
        if valid(f):
            i = int(f)
            return i if f - i == 0 else f
        else:
            return Invalid


@coercer
def positive_int_coerce(arg):
    '''Check if `arg` is a valid positive integer.'''
    res = int_coerce(arg)
    return res if res is Invalid or res >= 0 else Invalid


def create_int_range_coerce(min, max):
    '''Create a coercer to check integers between a range.'''
    min, max = check(int_coerce, min), check(int_coerce, max)
    if min < max:
        @coercer
        def inner(arg):
            'Check if `arg` is a valid integer between "{}" and "{}".'
            arg = int_coerce(arg)
            if valid(arg) and min <= arg <= max:
                return arg
            else:
                return Invalid
        inner.__name__ = str('int_between_{}_and_{}_coerce'.format(min, max))
        inner.__doc__ = inner.__doc__.format(min, max)
        return inner
    else:
        msg = '"{}" must be less than or equal "{}"'
        raise ValueError(msg.format(min, max))


# Identifiers and strings

# TODO: In Py3k "ña" is a valid identifier and this regex won't allow it
_IDENTIFIER_REGEX = regex_compile('(?i)^[_a-z][\w]*$')


@coercer
def identifier_coerce(arg):
    '''Check if `arg` is a valid Python identifier.

    .. note:: Only Python 2's version of valid identifier. This means that
              some Python 3 valid identifiers are not considered valid.  This
              helps to keep things working the same in Python 2 and 3.

    '''
    from xoutil.eight import string_types
    ok = isinstance(arg, string_types) and _IDENTIFIER_REGEX.match(arg)
    return str(arg) if ok else Invalid


_FULL_IDENTIFIER_REGEX = regex_compile('(?i)^[_a-z][\w]*([.][_a-z][\w]*)*$')


@coercer
def full_identifier_coerce(arg):
    '''Check if `arg` is a valid dotted Python identifier.

    See `identifier_coerce`:func: for what "validity" means.

    '''
    from xoutil.eight import string_types
    ok = isinstance(arg, string_types) and _FULL_IDENTIFIER_REGEX.match(arg)
    return str(arg) if ok else Invalid


@coercer
def names_coerce(arg):
    '''Check if `arg` is a valid tuple of valid object names (identifiers).

    If only one string is given, is returned as the only member of the
    resulting tuple.

    '''
    from xoutil.eight import string_types
    arg = (arg,) if isinstance(arg, string_types) else tuple(arg)
    return iterable(identifier_coerce)(arg)


# == Iterators ==

def create_unique_member_coerce(coerce, container):
    '''Useful to wrap member coercers when coercing containers.

    See `iterable`:class: and `mapping`:class:.

    Resulting coercer check that a member must be unique (not repeated) after
    it's coerced.

    For example::

      >>> from xoutil.values import (mapping,
      ...                            create_unique_member_coerce,
      ...                            int_coerce, float_coerce)

      >>> sample = {'1': 1, 2.0: '3', 1.0 + 0j: '4.1'}

      >>> dc = mapping(int_coerce, float_coerce)
      >>> dc(dict(sample))
      {1: 1.0, 2: 3.0}

      >>> dc = mapping(create_unique_member_coerce(int_coerce), float_coerce)
      >>> dc(dict(sample))
      Invalid

    '''
    coerce = check(coercer, coerce)

    @coercer
    def inner(arg):
        '''Check a member with "{}" coercer and warrant that is unique.'''
        # assert arg in container
        res = coerce(arg)
        if valid(res) and hash(res) != hash(arg) and res in container:
            res = Invalid
        return res

    cname = coercer_name(coerce)
    inner.__name__ = str('unique_member_{}_coerce'.format(cname))
    inner.__doc__ = inner.__doc__.format(cname)
    return inner


@coercer
def sized_coerce(arg):
    '''Return a valid sized iterable from `arg` (if valid).

    If `arg` is iterable but not sized, is converted to a list.  For example::

      >>> sized_coerce(i for i in range(1, 10, 2))
      [1, 3, 5, 7, 9]

      >>> s = {1, 2, 3}
      >>> sized_coerce(s) is s
      True

    '''
    from xoutil.collections import Iterable, Sized
    if isinstance(arg, Iterable):
        return arg if isinstance(arg, Sized) else list(arg)
    else:
        return Invalid


@coercer.adopt
class custom(object):
    '''Base class for any custom coercer.

    The field `inner` stores an internal data used for the custom coercer;
    could be a callable, an inner coercer, or a tuple of inner checkers if
    more than one is needed, ...

    The field `scope` stores the exit (not regular) condition: the value that
    fails or -if needed- a tuple with (exit-value, exit-coercer) or
    (error-value, error).  The exit condition is not always a failure, for
    example in `some`:class: it is the one that is valid among other inner
    coercers.  To understand better this think on (AND, OR) operators a chain
    of ANDs exits with the first failure and a chains of ORs exits with the
    first success.

    All custom coercers are callable (must redefine `__call__`:meth:)
    receiving one argument that must be coerced.  For example::

      >>> def foobar(*args):
      ...     coerce = pargs(int_coerce)
      ...     return coerce(args)

    This class has two protected fields (`_str_join` and `_repr_join`) that
    are used to call `coercer_name`:func: in `__str__`:meth: and
    `__repr__`:meth: special methods.

    '''
    __slots__ = ('inner', 'scope')

    _str_join = '_'
    _repr_join = ', '

    def __init__(self, *args, **kwargs):
        # This constructor is a placeholder for those custom coercers that can
        # return an instance of a different type in the `__new__`:meth:.
        from xoutil import Unset
        self.scope = Unset

    def __str__(self):
        name = coercer_name(self.inner, join=self._str_join)
        cls_name = type(self).__name__
        return str('{}_{}_coerce'.format(name, cls_name))

    def __repr__(self):
        name = coercer_name(self.inner, join=self._repr_join)
        cls_name = type(self).__name__
        return str('{}({})'.format(cls_name, name))

    def __call__(self, arg):
        return Invalid


class istype(custom):
    '''Pure type-checker.

    It's constructed from an argument valid for `types_tuple_coerce`:func:
    coercer.

    For example::

        >>> int_coerce = istype(int)

        >>> int_coerce(1)
        1

        >>> int_coerce('1')
        Invalid

        >>> number_coerce = istype((int, float, complex))

        >>> number_coerce(1.25)
        1.25

        >>> number_coerce('1.25')
        Invalid

    '''
    __slots__ = ('inner', 'scope')

    def __init__(self, types):
        super(istype, self).__init__()
        self.inner = check(types_tuple_coerce, types)

    def __call__(self, arg):
        return arg if isinstance(arg, self.inner) else Invalid


class typecast(istype):
    '''A type-caster.

    It's constructed from an argument valid for `types_tuple_coerce`:func:
    coercer.  Similar to `istype`:class: but try to convert the value if
    needed.

    For example::

        >>> int_cast = typecast(int)

        >>> int_cast('1')
        1

        >>> int_cast('1x')
        Invalid

    '''
    def __call__(self, arg):
        res = super(typecast, self).__call__(arg)
        i = 0
        while not valid(res) and i < len(self.inner):
            try:
                tp = self.inner[i]
                res = tp(arg)
                self.scope = tp
            except BaseException:
                i += 1
        return res


class safe(custom):
    '''Uses a function (or callable) in a safe way.

    Receives any callable that expects only one argument and returns another
    value; if that returned value is a Boolean, those functions are called
    predicates (See `xoutil.connote`:mod: for more information).

    The wrapped function is called in a safe way (inside try/except); if an
    exception is raised the coercer returns `Invalid` and it is saved in the
    instance field `scope`.

    '''
    def __init__(self, func):
        super(safe, self).__init__()
        self.inner = check(func, callable_coerce)

    def __call__(self, arg):
        try:
            return arg if self.inner(arg) else Invalid
        except BaseException as error:
            self.scope = (arg, error)
            return Invalid


class compose(custom):
    '''Returns the composition of several inner `coercers`.

    ``compose(f1, ... fn)`` is equivalent to f1(...(fn(arg))...)``.

    If no coercer is given return `identity_coerce`:func:.

    Could be considered an "AND" operator with some light differences because
    the nature of coercers: ordering the coercers is important when some can
    modify (adapt) original values.

    '''

    def __new__(cls, *coercers):
        coercers = pargs(coercer)(coercers)
        inner = tuple(check(coercer, c) for c in coercers
                      if c is not identity_coerce)
        if len(inner) > 1:
            self = super(compose, cls).__new__(cls)
            super(compose, self).__init__()
            self.inner = inner
            return self
        elif len(inner) == 1:
            return inner[0]
        else:
            return identity_coerce

    def __call__(self, arg):
        coercers = self.inner
        i = 0
        res = arg
        ok = True
        while ok and i < len(coercers):
            coerce = coercers[i]
            aux = coerce(res)
            if valid(aux):
                i += 1
            else:
                ok = False
                self.scope = (res, coerce)
            res = aux
        return res


class some(custom):
    '''Represent OR composition of several inner `coercers`.

    ``compose(f1, ... fn)`` is equivalent to f1(arg) or f2(arg) ... fn(arg)``
    in the sense "the first not `Invalid`".

    If no coercer is given return `void_coerce`:func:.

    '''

    def __new__(cls, *coercers):
        coercers = pargs(coercer)(coercers)
        inner = tuple(check(coercer, c) for c in coercers
                      if c is not void_coerce)
        if len(inner) > 1:
            self = super(some, cls).__new__(cls)
            super(some, self).__init__()
            self.inner = inner
            return self
        elif len(inner) == 1:
            return inner[0]
        else:
            return void_coerce

    def __init__(self, *coercers):
        pass

    def __call__(self, arg):
        coercers = self.inner
        i = 0
        res = Invalid
        while res is Invalid and i < len(coercers):
            coercer = coercers[i]
            value = coercer(arg)
            if valid(value):
                res = value
                self.scope = coercer
            else:
                i += 1
        return res


class combo(custom):
    '''Represent a zip composition of several inner `coercers`.

    An instance of this class is constructed from a sequence of coercers and
    the its purpose is coerce a sequence of values.  Return a sequence\
    [#type]_ where each item contains the i-th element from applying the i-th
    coercer to the i-th value from argument sequence::

      coercers -> (coercer-1, coercer-2, ... )
      values -> (value-1, value-2, ... )
      combo(coercers)(values) -> (coercer-1(value-1), coercer-2(value-2), ...)

    If any value is coerced invalid, the function returns `Invalid` and the
    combo's instance variable `scope` receives the duple ``(failed-value,
    failed-coercer)``.

    The returned sequence is truncated in length to the length of the shortest
    sequence (coercers or arguments).

    If no coercer is given, all sequences are coerced as empty.

    .. [#type] The returned sequence is of the same type as the argument
               sequence if possible.

    '''

    def __init__(self, *coercers):
        super(combo, self).__init__()
        coercers = pargs(coercer)(coercers)
        self.inner = tuple(check(coercer, c) for c in coercers)

    def __call__(self, arg):
        from xoutil import Unset
        from xoutil.collections import Iterable
        if isinstance(arg, Iterable):
            coercers = self.inner
            items = iter(arg)
            i = 0
            res = []
            ok = True
            while valid(res) and ok and i < len(coercers):
                item = next(items, Unset)
                if item is not Unset:
                    coerce = coercers[i]
                    value = coerce(item)
                    if valid(value):
                        res.append(value)
                        i += 1
                    else:
                        res = Invalid
                        self.scope = (item, coerce)
                else:
                    ok = False
            if valid(res):
                try:
                    res = type(arg)(res)
                except BaseException:
                    pass
        else:
            res = Invalid
        return res


class pargs(custom):
    '''Create a inner coercer that check variable argument passing.

    Created coercer closure must always receives an argument that is an valid
    iterable with all members coerced properly with the argument of this outer
    creator function.

    If the inner closure argument has only a member and this one is not
    properly coerced but it's an iterabled with all members that coerced well,
    this member will be the assumed iterable instead the original argument.

    In the following example::

      >>> from xoutil.values import (iterable, int_coerce)

      >>> def foobar(*args):
      ...     coerce = iterable(int_coerce)
      ...     return coerce(args)

      >>> args = (1, 2.0, '3.0')
      >>> foobar(*args)
      (1, 2, 3)

      >>> foobar(args)
      Invalid

    An example using `pargs`:class:\ ::

      >>> from xoutil.values import (pargs, int_coerce)

      >>> def foobar(*args):
      ...     # Below, "coercer" receives the returned "inner"
      ...     coerce = pargs(int_coerce)
      ...     return coerce(args)

      >>> args = (1, 2.0, '3.0')
      >>> foobar(*args)
      (1, 2, 3)

      >>> foobar(args)
      (1, 2, 3)

    The second form is an example of the real utility of this coercer
    closure: if by error a sequence is passed as it to a function that
    expect a variable number of argument, this coercer fixes it.

    Instance variable `scope` stores the last processed invalid argument.

    When executed, usually `arg` is a tuple received by a function as
    ``*args`` form::

    When executed, returns a tuple, or the same type of source iterable
    argument if possible.

    See `xoutil.params`:mod: for a more specialized and full function
    arguments conformer.

    See `combo`:class: for a combined coercer that  validate each member with
    a separate member coercer.

    '''

    def __init__(self, arg_coerce):
        super(pargs, self).__init__()
        self.inner = check(coercer, arg_coerce)

    def __call__(self, arg):
        from xoutil import Unset
        from xoutil.collections import Iterable
        coerce = self.inner
        if isinstance(arg, Iterable):
            arg = tuple(arg)
            if len(arg) == 1:
                item = arg[0]
                aux = coerce(item)
                if valid(aux):
                    res = (aux, )
                elif isinstance(item, Iterable):
                    res = Unset
                    arg = tuple(item)
                else:
                    self.scope = item
                    res = Invalid
            else:
                res = Unset
            if res is Unset:
                res = arg
                i = 0
                while valid(res) and i < len(res):
                    item = res[i]
                    new = coerce(item)
                    if valid(new):
                        if new is not item:
                            if isinstance(res, tuple):
                                res = list(res)
                            res[i] = new
                        i += 1
                    else:
                        self.scope = item
                        res = Invalid
                if valid(res):
                    res = tuple(res)
        else:
            res = Invalid
        return res


class iterable(custom):
    '''Create a inner coercer that coerces an `iterable` member a member.

    See constructor for more information.

    Return a list, or the same type of source iterable argument if possible.

    For example::

      >>> from xoutil.values import (iterable, int_coerce,
      ...                            create_unique_member_coerce)

      >>> sample = {'1', 1, '1.0'}

      >>> sc = iterable(int_coerce)
      >>> sc(set(sample)) == {1}
      True

    See `mapping`:class: for more details of this problem.  The equivalent
    safe example is::

      >>> member_coerce = create_unique_member_coerce(int_coerce, sample)
      >>> sc = iterable(member_coerce)
      >>> sc(set(sample))
      Invalid

    when executed coerces `arg` (an iterable) member a member using
    `member_coercer`. If any member coercion fails, the full execution also
    fails.

    There are three types of results when an instance is executed:
    (1) iterables that are coerced without modifications, (2) the modified
    ones but conserving its type, and (3) those that are returned in a list.

    '''

    def __init__(self, member_coerce, outer_coerce=None):
        '''Constructor for `iterable`:class: coercers.

        :param member_coerce: A coerce to check each iterable member.

        :param outer_coerce: A coerce to check the type of the entire
               iterable.  Normally a type or tuple of types subclases of
               ``collections.Iterable``.

        '''
        super(iterable, self).__init__()
        member_coerce = check(coercer, member_coerce)
        outer_coerce = compose(coercer(outer_coerce), sized_coerce)
        self.inner = (member_coerce, outer_coerce)

    def __call__(self, arg):
        from xoutil.collections import (Set, Sequence, MutableSequence)
        member_coerce, outer_coerce = self.inner
        modified = False
        aux = outer_coerce(arg)
        if valid(aux):
            arg = aux
            if isinstance(arg, Sequence):
                res = arg
                retyped = False
                mutable = isinstance(arg, MutableSequence)
            else:
                res = list(arg)
                retyped = mutable = True
            i = 0
            while valid(res) and i < len(res):
                item = res[i]
                new = member_coerce(item)
                if valid(new):
                    if new is not item:
                        if not mutable:
                            res = list(res)
                            retyped = mutable = True
                        res[i] = new
                        modified = True
                    i += 1
                else:
                    self.scope = item
                    res = Invalid
            if valid(res):
                if isinstance(arg, Set) and not modified:
                    res = arg
                elif retyped:
                    try:
                        res = type(arg)(res)
                    except BaseException:
                        pass
        else:
            self.scope = arg
            res = Invalid
        return res


class mapping(custom):
    '''Create a coercer to check dictionaries.

    Receives two coercers, one for keys and one for values.

    For example::

      >>> from xoutil.values import (mapping, int_coerce, float_coerce,
      ...                            create_unique_member_coerce)

      >>> sample = {'1': 1, 2.0: '3', 1.0 + 0j: '4.1'}

      >>> dc = mapping(int_coerce, float_coerce)
      >>> dc(dict(sample)) == {1: 1.0, 2: 3.0}
      True

    When coercing containers it's probable that members become repeated after
    coercing them.  This could be not desirable (mainly in sets and
    dictionaries). In those cases use `create_unique_member_coerce`:func: to
    wrap member coercer.  For example::

      >>> key_coerce = create_unique_member_coerce(int_coerce, sample)
      >>> dc = mapping(key_coerce, float_coerce)
      >>> dc(dict(sample))
      Invalid

    Above problem is because it's the same integer (same hash) coerced
    versions of ``'1'`` and ``1.0+0j``.

    This problem of objects of different types that have the same hash is a
    problem to use a example as below::

      >>> {1: int, 1.0: float, 1+0j: complex} == {1: complex}
      True

    '''
    _str_join = _repr_join = ':'

    def __new__(cls, key_coercer=None, value_coercer=None):
        '''Constructor for `mapping`:class: coercers.

        :param key_coercer: A coerce to check each one of the mapping keys.

        :param value_coercer: A coerce to check each one of corresponding
               mapping values.

        '''
        from xoutil.collections import Mapping
        if key_coercer is value_coercer is None:
            return coercer(Mapping)
        else:
            self = super(mapping, cls).__new__(cls)
            key_coercer = check(coercer, key_coercer)
            value_coercer = check(coercer, value_coercer)
            self.inner = (key_coercer, value_coercer)
            return self

    def __call__(self, arg):
        from xoutil.collections import (Mapping, MutableMapping)
        if isinstance(arg, Mapping):
            key_coercer, value_coercer = self.inner
            res = arg
            retyped = False
            mutable = isinstance(arg, MutableMapping)
            keys = list(res)
            i = 0
            while valid(res) and i < len(keys):
                key = keys[i]
                value = res[key]
                new_key = key_coercer(key)
                if valid(new_key):
                    new_value = value_coercer(value)
                    if valid(new_value):
                        if new_key is not key or new_value is not value:
                            if not mutable:
                                res = dict(res)
                                retyped = mutable = True
                            if key is not new_key:
                                del res[key]
                            res[new_key] = new_value
                        i += 1
                    else:
                        self.scope = ({key: value}, value_coercer)
                        res = Invalid
                else:
                    self.scope = ({key: value}, key_coercer)
                    res = Invalid
            if valid(res) and retyped:
                try:
                    res = type(arg)(res)
                except BaseException:
                    pass
        else:
            self.scope = ()
            res = Invalid
        return res


del sys, ABCMeta, metaclass, regex_compile, lwraps
