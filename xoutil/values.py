#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.values
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-07-15

'''Some generic coercers (or checkers) for value types.

This module coercion function are not related in any way to deprecated old
python feature, are similar to type checkers with two more concepts:

- Fit values to expected conventions.

- These functions must return `Invalid`\ [#pyni]_ special value to specify
  that expected fit is not possible.

.. [#pyni] We don't use Python classic `NotImplemented` special value in order
           to obtain False if the value is not coerced (`Invalid`).

A custom coercer could be created with closures, for an example see
`create_int_range_coerce`:func:.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        # unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


from re import compile as regex_compile
from xoutil.eight.meta import metaclass
from xoutil.logical import Logical as InvalidType


Invalid = InvalidType('Invalid')


def coercer(func):
    '''Decorator that mark a function as a coercer.'''
    try:
        func.__coercer__ = True
    except BaseException:
        func.__func__.__coercer__ = True
    return func


def check(coerce, arg):
    '''Coerce `arg`; if invalid raises a TypeError.

    See `create_int_range_coerce`:func: for an example.

    '''
    res = coerce(arg)
    if res is not Invalid:
        return res
    else:
        suffix = str('_coerce')
        name = coerce.__name__
        if name.endswith(suffix):
            name = name[:-len(suffix)]
        msg = 'Value "{}" is not coerced by "{}".'
        raise TypeError(msg.format(arg, name))


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
        if arg is not Invalid:
            res = int(arg)
            return res if arg - res == 0 else Invalid
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
            if arg is not Invalid and min <= arg <= max:
                return arg
            else:
                return Invalid
        inner.__name__ = str('int_between_{}_and_{}_coerce'.format(min, max))
        inner.__doc__ = inner.__doc__.format(min, max)
        return inner
    else:
        msg = '"{}" must be less than or equal "{}"'
        raise ValueError(msg.format(min, max))


@coercer
def type_checker_coerce(arg):
    '''Check if `arg` is a valid type checker.

    Type checkers are any type or tuple of types.

    '''
    from xoutil.eight import class_types as types
    if isinstance(arg, types):
        return (arg, )
    elif isinstance(arg, tuple) and all(isinstance(t, types) for t in arg):
        return arg
    else:
        return Invalid


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


class MetaCoercer(type):
    '''Meta-class for `Coercer`.

    This allow that a function marker with the decorator `coercer` is
    considered a valid instance of `Coercer`:class:; for example::

      >>> @coercer
      ... def age_coerce(arg):
      ...     res = int_coerce(arg)
      ...     return res if res is not Invalid and 0 < arg <= 120 else Invalid

      >>> isinstance(age_coerce, Coercer)
      True

    '''
    def __instancecheck__(self, instance):
        return getattr(instance, '__coercer__', False)


class Coercer(metaclass(MetaCoercer)):
    '''Create a coercer from a set of checker sources.

    Possible sources are:

    - A type or tuple of types: check if an object is a valid instance of
      given types; if valid return the same object; if not `Invalid`.

    - A checker (a callable\ [#pred]_): call the checker in a safe way (inside
      try / except) and return the value if the checker return True; if return
      False or an exception is raised, return `Invalid`.

    When `Invalid` is returned caused by an exception, that is saved in
    `last_exception` variable.

    This class also serves to check where any callable is a coercer or not.
    See `MetaCoercer`:class: for more information.

    .. [#pred] See `xoutil.connote.Predicate`:class: on how to define rich
               checkers.

    '''
    __slots__ = ('checker', 'last_exception')

    def __new__(cls, checker):
        from xoutil.eight import callable
        if isinstance(checker, Coercer):
            return checker
        else:
            aux = type_checker_coerce(checker)
            if aux is Invalid and callable(checker):
                aux = checker
            if aux is not Invalid:
                self = super(Coercer, cls).__new__(cls)
                super(Coercer, self).__init__()
                self.checker = aux
                self.last_exception = None
                return self
            else:
                return Invalid

    def __init__(self, checker):
        pass

    def __call__(self, arg):
        checker = self.checker
        if isinstance(checker, tuple):
            return arg if isinstance(arg, checker) else Invalid
        else:
            try:
                return arg if checker(arg) else Invalid
            except BaseException as error:
                self.last_exception = (error, arg)
                return Invalid


del metaclass, regex_compile
