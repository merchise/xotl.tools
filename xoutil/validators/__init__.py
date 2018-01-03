#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Some generic value validators and regular expressions and validation
functions for several identifiers.

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

# TODO: Check next import, it looks like one of the modules must be deprecated
from xoutil.validators.identifiers import (is_valid_identifier,   # noqa
                                           check_identifier,
                                           is_valid_full_identifier,
                                           is_valid_public_identifier,
                                           is_valid_slug)


def _adorn_checker_name(name):
    '''Make more attractive or legible a checker name.'''
    res = name.replace('_AND_', ' & ')
    res = res.replace('_OR_', ' | ')
    return res.replace('<lambda>', '<λ>')


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
        from xoutil.future.inspect import safe_name
        res = safe_name(checker, affirm=True)
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
# TODO: Migrate to a class
def predicate(*checkers, **kwargs):
    '''Return a validation checker for types and simple conditions.

    :param checkers: A variable number of checkers; each one could be:

        - A type, or tuple of types, to test valid values with
          ``isinstance(value, checker)``

        - A set or mapping of valid values, the value is valid if contained in
          the checker.

        - A tuple of other inner checkers, if any of the checkers validates a
          value, the value is valid (OR).

        - A list of other inner checkers, all checkers must validate the value
          (AND).

        - A callable that receives the value and returns True if the value is
          valid.

        - ``True`` and ``False`` could be used as checkers always validating
          or invalidating the value.

        An empty list or no checker is synonym of ``True``, an empty tuple,
        set or mapping is synonym of ``False``.

    :param name: Keyword argument to be used in case of error; will be the
        argument of `ValueError` exception; could contain the placeholders
        ``{value}`` and ``{type}``; a default value is used if this argument
        is not given.

    :param force_name: Keyword argument to force a name if not given.

    In order to obtain good documentations, use proper names for functions and
    lambda arguments.

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
    from xoutil.symbols import boolean
    from xoutil.future.collections import Set, Mapping

    def inner(obj):
        '''Check is `obj` is a valid instance for a set of checkers.'''

        def valid(chk):
            if isinstance(chk, boolean):
                res = bool(chk)
            elif isinstance(chk, type):
                res = isinstance(obj, chk)
            elif isinstance(chk, tuple):
                if all(isinstance(c, type) for c in chk):
                    res = isinstance(obj, chk)
                else:
                    res = any(valid(c) for c in chk)
            elif isinstance(chk, list):
                res = all(valid(c) for c in chk)
            elif isinstance(chk, (Set, Mapping)):
                res = obj in chk
            else:
                res = chk(obj)
            return res

        # XXX: WTF, must be ``all(valid(chk) for chk in checkers)``
        return next((chk for chk in checkers if not valid(chk)), None) is None

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
        from xoutil.future.inspect import safe_name
        if not msg:
            # TODO: Use the name of validator with `inspect.getattr_static`
            # when `xoutil.future` is ready
            msg = 'Invalid value "%s" of type "%s"'
        msg = msg.format(value=value, type=safe_name(value, affirm=True))
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
           ``{value}`` and ``{type}``; a default value is used if this
           argument is not given.

    :param msg: an alias for "message"

    :param extra_checkers: In order to create validators using `partial`.
           Must be a tuple.

    Keyword arguments are not validated to be correct.

    This function could be used with type-definitions for arguments, see
    `xoutil.fp.prove.semantic.TypeCheck`:class:.

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
    extra_checkers = kwargs.get('extra_checkers', ())
    pred = predicate(*(checkers + extra_checkers))
    if pred(value):
        return value
    else:
        from xoutil.future.itertools import multi_get as get
        from xoutil.future.inspect import safe_name
        msg = next(get(kwargs, 'message', 'msg'), 'Invalid {type}: {value}!')
        msg = msg.format(value=value, type=safe_name(value, affirm=True))
        raise ValueError(msg)


def check_no_extra_kwargs(kwargs):
    '''Check that no extra keyword arguments are still not processed.

    For example::

      >>> from xoutil.validators import check_no_extra_kwargs
      >>> def only_safe_arg(**kwargs):
      ...     safe = kwargs.pop('safe', False)
      ...     check_no_extra_kwargs(kwargs)
      ...     print('OK for safe:', safe)

    '''
    if kwargs:
        plural = '' if len(kwargs) == 1 else 's'
        msg = 'Unexpected keyword argument%s: "%s"!'
        raise TypeError(msg % (plural, ', '.join(kwargs)))
