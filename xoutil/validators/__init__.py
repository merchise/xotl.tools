# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.validators
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# Copyright (c) 2011, 2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created 2014-05-06

'''Some generic value validators and regular expressions and validation
functions for several identifiers.

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

from .identifiers import (is_valid_identifier,   # noqa
                          check_identifier,
                          is_valid_full_identifier,
                          is_valid_public_identifier,
                          is_valid_slug)


def _get_checker_name(checker):
    '''Return a nice name for a `checker`.

    A `checker` could be a type, a tuple of types, a callable or a list of
    other checkers.

    '''
    l = lambda o: str('(%s)' % o.join(_get_checker_name(c) for c in checker))
    if isinstance(checker, list):
        return l('_AND_')
    elif isinstance(checker, tuple):
        return l('_OR_')
    else:
        from xoutil.inspect import type_name
        res = type_name(checker)
        if not isinstance(checker, type):
            assert callable(checker)
            if 'lambda' in res:
                from inspect import getargspec
                args = getargspec(checker).args
                assert len(args) == 1
                res = str('%s(%s)' % (res, args[0]))
        return res


def is_type(cls):
    '''Return a validator with the same name as the type given as argument
    `value`.

    :param cls: Class or type or tuple of several types.

    '''
    def inner(obj):
        '''Check is a value object is a valid instance of (%s).'''
        return isinstance(obj, cls)

    name = _get_checker_name(cls)
    inner.__name__ = name
    inner.__doc__ = inner.__doc__ % name
    return inner


# TODO: With this new function, `is_type` could be deprecated
def predicate(*checkers, **kwargs):
    '''Return a validation checker for types and simple conditions.

    :param checkers: A variable number of checkers, each one could be a type,
        a tuple of types, a callable that receives the value and returns if
        the value is valid, or a list of other inner checkers.  In order the
        value is considered valid, all checkers must validate the value.  True
        and False could be used as checkers always validating or invalidating
        the value.  An empty list or no checker is synonym of True, an empty
        tuple is synonym of False.

    :param name: Keyword argument to be used in case of error; will be the
        argument of `ValueError` exception; could contain the placeholders
        ``{value}`` and ``{type}``; a default value is used if this argument
        is not given.

    :param force_name: Keyword argument to force a name is not given.

    With this function could be built real type checkers, for example::

      >>> is_valid_age = predicate((int, float), lambda age: 0 < age <= 120)
      >>> is_valid_age(100)
      True

      >>> is_valid_age(130)
      False

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
    def inner(obj):
        '''Check is `obj` is a valid instance for a set of checkers.'''

        def fail(chk):
            if isinstance(chk, bool):
                res = chk
            elif isinstance(chk, (type, tuple)):
                res = isinstance(obj, chk)
            elif isinstance(chk, list):
                res = predicate(*chk)(obj)
            else:
                res = chk(obj)
            return not res

        return next((chk for chk in checkers if fail(chk)), None) is None

    name = kwargs.get('name')
    if name is None and kwargs.get('force_name'):
        name = _get_checker_name(list(checkers))
    if name is not None:
        inner.__name__ = name
    return inner


def check(value, validator, msg=None):
    '''Check a `value` with a `validator`.

    Argument `validator` could be a callable, a type, or a tuple of types.

    Return True if the value is valid.

    Examples::

      >>> check(1, int)
      True

      >>> check(10, lambda x: x <= 100, 'must be less than or equal to 100')
      True

      >>> check(11/2, (int, float))
      True

    '''
    if isinstance(validator, (type, tuple)):
        checker = is_type(validator)
    else:
        checker = validator
    if checker(value):
        return True
    else:
        from xoutil.inspect import type_name
        if not msg:
            # TODO: Use the name of validator with `inspect.getattr_static`
            # when `xoutil.future` is ready
            msg = 'Invalid value "%s" of type "%s"'
        msg = msg.format(value=value, type=type_name(value, affirm=True))
        raise ValueError(msg)


# TODO: deprecate `check` in favor of `ok`.
def ok(value, *checkers, **kwargs):
    '''Validate a value with several checkers.

    Return the value if it is Ok, or raises an `ValueError` exception if not.

    Arguments:

    :param value: the value to validate

    :param checkers: a variable number of checkers (at least one), each one
        could be a type, a tuple of types of a callable that receives the
        value and returns if the value is valid or not.  In order the value is
        considered valid, all checkers must validate the value.

    :param message: keyword argument to be used in case of error; will be the
        argument of `ValueError` exception; could contain the placeholders
        ``{value}`` and ``{type}``; a default value is used if this argument
        is not given.

    :param msg: an alias for "message"

    Keyword arguments are not validated to be correct.

    This function could be used with type-definitions for arguments, see
    :class:`TypeChecker`.

    Examples::

      >>> ok(1, int)
      1

      >>> ok(10, int, lambda x: x < 100, message='Must be integer under 100')
      10

      >>> ok(11/2, (int, float))
      5.5

      >>> ok(11/2, int, float)
      5.5

      >>> try:
      ...     res = ok(11/2, int)
      ... except ValueError:
      ...     res = '---'
      >>> res
      '---'

    '''
    pred = predicate(*checkers)
    if pred(value):
        return value
    else:
        from xoutil.iterators import multi_get as get
        from xoutil.inspect import type_name
        msg = next(get(kwargs, 'message', 'msg'), 'Invalid {type}: {value}!')
        msg = msg.format(value=value, type=type_name(value, affirm=True))
        raise ValueError(msg)
