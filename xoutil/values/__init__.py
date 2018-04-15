#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Some generic coercers (or checkers) for value types.

This module coercion function are not related in any way to deprecated old
python feature, are similar to a combination of object mold/check:

- *Mold* - Fit values to expected conventions.

- *Check* - These functions must return `nil`\ [#pyni]_ special value to
  specify that expected fit is not possible.

.. [#pyni] We don't use Python classic `NotImplemented` special value in order
           to obtain False if the value is not coerced (`nil`).

A custom coercer could be created with closures, for an example see
`create_int_range_coerce`:func:.

This module uses `Unset` value to define absent -not being specified-
arguments.

Also contains sub-modules to obtain, convert and check values of common types.

.. versionadded:: 1.7.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import re
from xoutil.eight.abc import ABCMeta
from xoutil.future.functools import lwraps
from xoutil.symbols import boolean, Unset
from xoutil.fp.prove import vouch

from xoutil.deprecation import deprecate_linked
deprecate_linked(check='xoutil.values')
del deprecate_linked


_coercer_decorator = lwraps(__coercer__=True)    # FIX: refactor


class logical(boolean):
    '''Represent Common Lisp two special values `t` and `nil`.

    Include redefinition of `__call__`:meth: to check values with special
    semantic:

    - When called as ``t(arg)``, check if `arg` is not `nil` returning a
      logical true: the same argument if `arg` is nil or a true boolean value,
      else return `t`.  That means that `False` or `0` are valid true values
      for Common Lisp but not for Python.

    - When called as ``nil(arg)``, check if `arg` is `nil` returning `t` or
      `nil` if not.

    Constructor could receive a valid name ('nil' or 't') or any other
    ``boolean`` instance.

    '''
    __slots__ = ()
    _valid = {'nil': False, 't': True}

    def __new__(cls, arg):
        from xoutil.symbols import boolean
        from xoutil.symbols import Invalid
        name = ('t' if arg else 'nil') if isinstance(arg, boolean) else arg
        value = cls._valid.get(name, Invalid)
        if value is not Invalid:
            return super().__new__(cls, name, value)
        else:
            msg = 'retrieving invalid logical instance "{}"'
            raise TypeError(msg.format(arg))

    def __call__(self, arg):
        if self:    # self is t
            return arg if arg or arg is nil else self
        else:    # self is nil
            return t if arg is self else self


nil, t = logical('nil'), logical('t')


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
                super().__instancecheck__(instance))


class coercer(metaclass=MetaCoercer):
    '''Special coercer class.

    This class has several facets:

    - Pure type-checkers when a type or tuple of types are received as
      argument.  See `istype`:class: for more information.

    - Return equivalent coercer from some special values:

      * Any true value -> identity_coerce

      * Any false or empty value -> void_coerce

    - A decorator for functions; when a function is given, decorate it to
      become a coercer.  The mark itself is not enough, functions intended to
      be coercers must fulfills the protocol (not to produce exception and
      return `nil` on fails).  For example::

        >>> @coercer
        ... def age_coerce(arg):
        ...     res = int_coerce(arg)
        ...     return res if t(res) and 0 < arg <= 120 else nil

        # TODO: Change next, don't use isinstance
        >>> isinstance(age_coerce, coercer)
        True

    '''
    __slots__ = ()
    __coercer__ = True

    def __new__(cls, source):
        from types import FunctionType as function
        from xoutil.symbols import boolean
        if source == 1 and isinstance(source, boolean):
            return identity_coerce
        elif source is None or (source == 0 and isinstance(source, boolean)):
            return void_coerce
        elif isinstance(source, coercer):    # TODO: don't use isinstance
            return source
        elif isinstance(source, (function, staticmethod, classmethod)):
            return _coercer_decorator(source)
        else:
            inner = types_tuple_coerce(source)
            return istype(inner) if inner else nil


def coercer_name(arg, join=None):
    '''Get the name of a coercer.

    :param arg: Coercer to get the name.  Also processes collections (tuple,
           list, or set) of coercers.  Any other value is considered invalid
           and raises an exception.

    :param join: When a collection is used; if this argument is None a
           collection of names is returned, if not None then is used to join
           the items in a resulting string.

           For example::

             >>> coercer_name((int_coerce, float_coerce))
             ('int', 'float')

             >>> coercer_name((int_coerce, float_coerce), join='-')
             'int-float'

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
        except Exception:
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
    '''Always `nil`.'''
    return nil


@coercer
def type_coerce(arg):
    '''Check if `arg` is a valid type.'''
    from xoutil.eight import class_types
    return arg if isinstance(arg, class_types) else nil


@coercer
def types_tuple_coerce(arg):
    '''Check if `arg` is valid for `isinstance` or `issubclass` 2nd argument.

    Type checkers are any class, a type or tuple of types.  For example::

      >>> types_tuple_coerce(object) == (object,)
      True

      >>> types_tuple_coerce((int, float)) == (int, float)
      true

      >>> types_tuple_coerce('not-a-type') is nil
      True

    See `type_coerce` for more information.

    '''
    if t(type_coerce(arg)):
        return (arg, )
    elif isinstance(arg, tuple) and all(t(type_coerce(tp)) for tp in arg):
        return arg
    else:
        return nil


@coercer
def callable_coerce(arg):
    '''Check if `arg` is a callable object.'''
    from xoutil.eight import callable
    return arg if callable(arg) else nil


@coercer
def file_coerce(arg):
    '''Check if `arg` is a file-like object.'''
    from xoutil.eight.io import is_file_like
    return arg if is_file_like(arg) else nil


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
            return nil
    elif isinstance(arg, complex):
        return arg.real if arg.imag == 0 else nil
    else:
        return nil


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
        if t(arg):
            res = int(arg)
            return res if arg - res == 0 else nil
        else:
            return nil


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
        if t(f):
            i = int(f)
            return i if f - i == 0 else f
        else:
            return nil


@coercer
def positive_int_coerce(arg):
    '''Check if `arg` is a valid positive integer.'''
    res = int_coerce(arg)
    return res if res is nil or res >= 0 else nil


def create_int_range_coerce(min, max):
    '''Create a coercer to check integers between a range.'''
    min, max = vouch(int_coerce, min), vouch(int_coerce, max)
    if min < max:
        @coercer
        def inner(arg):
            'Check if `arg` is a valid integer between "{}" and "{}".'
            arg = int_coerce(arg)
            if t(arg) and min <= arg <= max:
                return arg
            else:
                return nil
        inner.__name__ = str('int_between_{}_and_{}_coerce'.format(min, max))
        inner.__doc__ = inner.__doc__.format(min, max)
        return inner
    else:
        msg = '"{}" must be less than or equal "{}"'
        raise ValueError(msg.format(min, max))


# Identifiers and strings

# TODO: In Py3k "ña" is a valid identifier and this regex won't allow it
_IDENTIFIER_REGEX = re.compile('(?i)^[_a-z][\w]*$')


@coercer
def identifier_coerce(arg):
    '''Check if `arg` is a valid Python identifier.

    .. note:: Only Python 2's version of valid identifier. This means that
              some Python 3 valid identifiers are not considered valid.  This
              helps to keep things working the same in Python 2 and 3.

    '''
    # TODO: Consider use ``is_python2_identifier(arg) or nil`` in module
    # `xoutil.eight.string`.
    from xoutil.eight import string_types
    ok = isinstance(arg, string_types) and _IDENTIFIER_REGEX.match(arg)
    return str(arg) if ok else nil


_FULL_IDENTIFIER_REGEX = re.compile('(?i)^[_a-z][\w]*([.][_a-z][\w]*)*$')


@coercer
def full_identifier_coerce(arg):
    '''Check if `arg` is a valid dotted Python identifier.

    See `identifier_coerce`:func: for what "validity" means.

    '''
    from xoutil.eight import string_types
    ok = isinstance(arg, string_types) and _FULL_IDENTIFIER_REGEX.match(arg)
    return str(arg) if ok else nil


@coercer
def names_coerce(arg):
    '''Check `arg` as a tuple of valid object names (identifiers).

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

      >>> from xoutil.values import (mapping, create_unique_member_coerce,
      ...                            int_coerce, float_coerce)

      >>> sample = {'1': 1, 2.0: '3', 1.0 + 0j: '4.1'}

      >>> dc = mapping(int_coerce, float_coerce)
      >>> dc(dict(sample))
      {1: 1.0, 2: 3.0}

      >>> dc = mapping(create_unique_member_coerce(int_coerce), float_coerce)
      >>> dc(dict(sample))
      nil

    '''
    coerce = vouch(coercer, coerce)

    @coercer
    def inner(arg):
        '''Check a member with "{}" coercer and warrant that is unique.'''
        # assert arg in container
        res = coerce(arg)
        if t(res) and hash(res) != hash(arg) and res in container:
            res = nil
        return res

    cname = coercer_name(coerce)
    inner.__name__ = str('unique_member_{}_coerce'.format(cname))
    inner.__doc__ = inner.__doc__.format(cname)
    return inner


@coercer
def sized_coerce(arg):
    '''Return a valid sized iterable from `arg`.

    If `arg` is iterable but not sized, is converted to a list.  For example::

      >>> sized_coerce(i for i in range(1, 10, 2))
      [1, 3, 5, 7, 9]

      >>> s = {1, 2, 3}
      >>> sized_coerce(s) is s
      True

    '''
    from collections import Iterable, Sized
    if isinstance(arg, Iterable):
        return arg if isinstance(arg, Sized) else list(arg)
    else:
        return nil


@coercer.adopt
class custom:
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
        return nil

    @classmethod
    def flatten(cls, obj, avoid=Unset):
        '''Flatten a coercer set.

        :param obj: Could be a coercer representing other inner coercers, or a
               tuple or list containing coercers.

        '''
        aux = obj.inner if isinstance(obj, cls) else obj
        if isinstance(aux, (tuple, list)):
            if not types_tuple_coerce(aux):
                res = (i for l in map(cls.flatten, aux) for i in l)
            else:
                res = (coercer(aux),)
        else:
            res = (aux,)
        if avoid is not Unset:
            res = (i for i in res if i is not avoid)
        return tuple(res)


class istype(custom):
    '''Pure type-checker.

    It's constructed from an argument valid for `types_tuple_coerce`:func:
    coercer.

    For example::

        >>> int_coerce = istype(int)

        >>> int_coerce(1)
        1

        >>> int_coerce('1')
        nil

        >>> number_coerce = istype((int, float, complex))

        >>> number_coerce(1.25)
        1.25

        >>> number_coerce('1.25')
        nil

    '''
    __slots__ = ()

    def __new__(cls, types):
        if types:
            self = super().__new__(cls)
            self.inner = vouch(types_tuple_coerce, types)
            return self
        else:
            return void_coerce

    def __call__(self, arg):
        return arg if isinstance(arg, self.inner) else nil


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
        nil

    '''
    __slots__ = ()

    def __call__(self, arg):
        res = super().__call__(arg)
        i = 0
        while not t(res) and i < len(self.inner):
            try:
                tp = self.inner[i]
                res = tp(arg)
                self.scope = tp
            except Exception:
                i += 1
        return res


class safe(custom):
    '''Uses a function (or callable) in a safe way.

    Receives a coercer that expects only one argument and returns another
    value.

    If the returned value is a ``boolean`` (maybe the coercer is a predicate),
    it's converted to a ``logical`` instance.

    The wrapped coercer is called in a safe way (inside try/except); if an
    exception is raised the coercer returns ``nil`` and the error is saved in
    the instance attribute ``scope``.

    '''
    __slots__ = ()

    def __init__(self, func):
        super().__init__()
        self.inner = vouch(coercer, func)

    def __call__(self, arg):
        try:
            from xoutil.symbol import boolean
            res = self.inner(arg)
            return logical(res) if isinstance(res, boolean) else res
        except Exception as error:
            self.scope = (arg, error)
            return nil


class compose(custom):
    '''Returns the composition of several inner `coercers`.

    ``compose(f1, ... fn)`` is equivalent to f1(...(fn(arg))...)``.

    If no coercer is given return `identity_coerce`:func:.

    Could be considered an "AND" operator with some light differences because
    the nature of coercers: ordering the coercers is important when some can
    modify (adapt) original values.

    If no value results in `coercers`, a default coercer could be given as a
    keyword argument; `identity_coerce` is assumed if missing.

    '''
    __slots__ = ()

    def __new__(cls, *coercers, **kwds):
        inner = cls.flatten(coercers, avoid=identity_coerce)
        count = len(inner)
        if count > 1:
            self = super().__new__(cls)
            self.inner = inner
            return self
        elif count == 1:
            return inner[0]
        else:
            res = kwds.pop('default', identity_coerce)
            if not kwds:
                return res
            else:
                msg = '`compose` got unexpected keyword argument(s) "{}"'
                raise TypeError(msg.format(set(kwds)))

    def __call__(self, arg):
        coercers = self.inner
        i = 0
        res = arg
        ok = True
        while ok and i < len(coercers):
            coerce = coercers[i]
            aux = coerce(res)
            if t(aux):
                i += 1
            else:
                ok = False
                self.scope = (res, coerce)
            res = aux
        return res


class some(custom):
    '''Represent OR composition of several inner `coercers`.

    ``compose(f1, ... fn)`` is equivalent to f1(arg) or f2(arg) ... fn(arg)``
    in the sense "the first not `nil`".

    If no coercer is given return `void_coerce`:func:.

    '''
    __slots__ = ()

    def __new__(cls, *coercers):
        inner = cls.flatten(coercers, avoid=void_coerce)
        if len(inner) > 1:
            self = super().__new__(cls)
            self.inner = inner
            return self
        elif len(inner) == 1:
            return inner[0]
        else:
            return void_coerce

    def __call__(self, arg):
        coercers = self.inner
        i = 0
        res = nil
        while res is nil and i < len(coercers):
            coercer = coercers[i]
            value = coercer(arg)
            if t(value):
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

    If any value is coerced invalid, the function returns `nil` and the
    combo's instance variable `scope` receives the duple ``(failed-value,
    failed-coercer)``.

    The returned sequence is truncated in length to the length of the shortest
    sequence (coercers or arguments).

    If no coercer is given, all sequences are coerced as empty.

    .. [#type] The returned sequence is of the same type as the argument
               sequence if possible.

    '''
    __slots__ = ()

    def __init__(self, *coercers):
        super().__init__()
        coercers = pargs(coercer)(coercers)
        self.inner = tuple(vouch(coercer, c) for c in coercers)

    def __call__(self, arg):
        from collections import Iterable
        if isinstance(arg, Iterable):
            coercers = self.inner
            items = iter(arg)
            i = 0
            res = []
            ok = True
            while t(res) and ok and i < len(coercers):
                item = next(items, Unset)
                if item is not Unset:
                    coerce = coercers[i]
                    value = coerce(item)
                    if t(value):
                        res.append(value)
                        i += 1
                    else:
                        res = nil
                        self.scope = (item, coerce)
                else:
                    ok = False
            if t(res):
                try:
                    res = type(arg)(res)
                except Exception:
                    pass
        else:
            res = nil
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
      nil

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
    ``*args`` form.

    When executed, returns a tuple, or the same type of source iterable
    argument if possible.

    See `xoutil.params`:mod: for a more specialized and full function
    arguments conformer.

    See `combo`:class: for a combined coercer that  validate each member with
    a separate member coercer.

    '''
    __slots__ = ()

    def __init__(self, arg_coerce):
        super().__init__()
        self.inner = vouch(coercer, arg_coerce)

    def __call__(self, arg):
        from collections import Iterable
        coerce = self.inner
        if isinstance(arg, Iterable):
            arg = tuple(arg)
            if len(arg) == 1:
                item = arg[0]
                aux = coerce(item)
                if t(aux):
                    res = (aux, )
                elif isinstance(item, Iterable):
                    res = Unset
                    arg = tuple(item)
                else:
                    self.scope = item
                    res = nil
            else:
                res = Unset
            if res is Unset:
                res = arg
                i = 0
                while t(res) and i < len(res):
                    item = res[i]
                    new = coerce(item)
                    if t(new):
                        if new is not item:
                            if isinstance(res, tuple):
                                res = list(res)
                            res[i] = new
                        i += 1
                    else:
                        self.scope = item
                        res = nil
                if t(res):
                    res = tuple(res)
        else:
            res = nil
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
      nil

    when executed coerces `arg` (an iterable) member a member using
    `member_coercer`. If any member coercion fails, the full execution also
    fails.

    There are three types of results when an instance is executed:
    (1) iterables that are coerced without modifications, (2) the modified
    ones but conserving its type, and (3) those that are returned in a list.

    '''
    __slots__ = ()

    def __init__(self, member_coerce, outer_coerce=True):
        '''Constructor for `iterable`:class: coercers.

        :param member_coerce: A coerce to check each iterable member.

        :param outer_coerce: A coerce to check the type of the entire
               iterable.  Normally a type or tuple of types subclases of
               ``collections.Iterable``.

        '''
        super().__init__()
        member_coerce = vouch(coercer, member_coerce)
        outer_coerce = compose(coercer(outer_coerce), sized_coerce)
        self.inner = (member_coerce, outer_coerce)

    def __call__(self, arg):
        from collections import (Set, Sequence, MutableSequence)
        member_coerce, outer_coerce = self.inner
        modified = False
        aux = outer_coerce(arg)
        if t(aux):
            arg = aux
            if isinstance(arg, Sequence):
                res = arg
                retyped = False
                mutable = isinstance(arg, MutableSequence)
            else:
                res = list(arg)
                retyped = mutable = True
            i = 0
            while t(res) and i < len(res):
                item = res[i]
                new = member_coerce(item)
                if t(new):
                    if new is not item:
                        if not mutable:
                            res = list(res)
                            retyped = mutable = True
                        res[i] = new
                        modified = True
                    i += 1
                else:
                    self.scope = item
                    res = nil
            if t(res):
                if isinstance(arg, Set) and not modified:
                    res = arg
                elif retyped:
                    try:
                        res = type(arg)(res)
                    except Exception:
                        pass
        else:
            self.scope = arg
            res = nil
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
      nil

    Above problem is because it's the same integer (same hash) coerced
    versions of ``'1'`` and ``1.0+0j``.

    This problem of objects of different types that have the same hash is a
    problem to use a example as below::

      >>> {1: int, 1.0: float, 1+0j: complex} == {1: complex}
      True

    '''
    __slots__ = ()
    _str_join = _repr_join = ':'

    def __new__(cls, key_coercer=Unset, value_coercer=Unset):
        '''Constructor for `mapping`:class: coercers.

        :param key_coercer: A coerce to check each one of the mapping keys.

        :param value_coercer: A coerce to check each one of corresponding
               mapping values.

        '''
        from collections import Mapping
        if key_coercer is value_coercer is Unset:
            return coercer(Mapping)
        else:
            self = super().__new__(cls)
            key_coercer = vouch(coercer, key_coercer or True)
            value_coercer = vouch(coercer, value_coercer or True)
            self.inner = (key_coercer, value_coercer)
            return self

    def __call__(self, arg):
        from collections import (Mapping, MutableMapping)
        if isinstance(arg, Mapping):
            key_coercer, value_coercer = self.inner
            res = arg
            retyped = False
            mutable = isinstance(arg, MutableMapping)
            keys = list(res)
            i = 0
            while t(res) and i < len(keys):
                key = keys[i]
                value = res[key]
                new_key = key_coercer(key)
                if t(new_key):
                    new_value = value_coercer(value)
                    if t(new_value):
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
                        res = nil
                else:
                    self.scope = ({key: value}, key_coercer)
                    res = nil
            if t(res) and retyped:
                try:
                    res = type(arg)(res)
                except Exception:
                    pass
        else:
            self.scope = ()
            res = nil
        return res


del re, ABCMeta, lwraps
