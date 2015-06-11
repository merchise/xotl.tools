# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.decorator
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# Copyright (c) 2009-2012 Medardo Rodríguez
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#

'''Some useful decorators.'''

# TODO: reconsider all this module


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

import sys

from functools import wraps
from types import FunctionType as function

from .meta import decorator as _decorator


from xoutil.names import strlist as strs
__all__ = strs('decorator', 'AttributeAlias', 'settle', 'namer', 'aliases',
               'assignment_operator', 'instantiate', 'memoized_property',
               'memoized_instancemethod', 'reset_memoized')
del strs


class AttributeAlias(object):
    '''Descriptor to create aliases for object attributes.

    This descriptor is mainly to be used internally by :func:`aliases`
    decorator.

    '''

    def __init__(self, attr_name):
        super(AttributeAlias, self).__init__()
        self.attr_name = attr_name

    def __get__(self, instance, owner):
        return getattr(instance or owner, self.attr_name)

    def __set__(self, instance, value):
        setattr(instance, self.attr_name, value)

    def __delete__(self, instance):
        delattr(instance, self.attr_name)


def settle(**kwargs):
    '''Returns a decorator that sets different attribute values to the
    decorated target (function or class).

    Usage::

       >>> @settle(name='Name')
       ... class Person(object):
       ...    pass

       >>> Person.name
       'Name'

    '''
    def inner(target):
        from xoutil.eight import iteritems
        for key, value in iteritems(kwargs):
            setattr(target, key, value)
        return target
    return inner


def namer(name, **kwargs):
    '''Like :func:`settle`, but name is a positional argument and is assigned
    to the attribute ``__name__``.

    Usage::

        >>> @namer('Identity', custom=1)
        ... class I(object):
        ...    pass

        >>> I.__name__
        'Identity'

        >>> I.custom
        1

    '''
    return settle(__name__=name, **kwargs)


def aliases(*names, **kwargs):
    '''In a class, create an :class:`AttributeAlias` descriptor for each
    definition as keyword argument (alias=existing_attribute).

    If "names" are given, then the definition context is looked and are
    assigned to it the same decorator target with all new names::

        >>> @aliases('foo', 'bar')
        ... def foobar(*args):
        ...     'This function is added to its module with two new names.'

    '''
    def inner(target):
        '''Direct closure decorator that settle several attribute aliases.
        '''
        if kwargs:
            assert isinstance(target, type), '"target" must be a class.'
        if names:
            _locals = sys._getframe(1).f_locals
            for name in names:
                _locals[str(name)] = target
        if kwargs:
            for alias, field in kwargs.iteritems():
                setattr(target, alias, AttributeAlias(field))
        return target
    return inner


@_decorator
def assignment_operator(func, maybe_inline=False):
    '''Makes a function that receives a name, and other args to get its first
    argument (the name) from an assigment operation, meaning that it if its
    used in a single assignment statement the name will be taken from the left
    part of the ``=`` operator.

    .. warning:: This function is dependant of CPython's implementation of the
                 language and won't probably work on other implementations.
                 Use only you don't care about portability, but use sparingly
                 (in case you change your mind about portability).

    '''
    import inspect
    import ast

    if not isinstance(func, function):
        raise TypeError('"func" must be a function.')

    @wraps(func)
    def inner(*args):
        frm = sys._getframe(1)
        filename, line, funcname, src_lines, idx = inspect.getframeinfo(frm)
        try:
            sourceline = src_lines[idx].strip()
            parsed_line = ast.parse(sourceline, filename).body[0]
            assert maybe_inline or isinstance(parsed_line, ast.Assign)
            if isinstance(parsed_line, ast.Assign):
                assert len(parsed_line.targets) == 1
                assert isinstance(parsed_line.targets[0], ast.Name)
                name = parsed_line.targets[0].id
            elif maybe_inline:
                assert isinstance(parsed_line, ast.Expr)
                name = None
            else:
                assert False
            return func(name, *args)
        except (AssertionError, SyntaxError):
            if maybe_inline:
                return func(None, *args)
            else:
                return func(*args)
        finally:
            del filename, line, funcname, src_lines, idx
    return inner


@_decorator
def instantiate(target, *args, **kwargs):
    '''Some singleton classes must be instantiated as part of its declaration
    because they represents singleton objects.

    Every argument, positional or keyword, is passed as such when invoking the
    target. The following two code samples show two cases::

       >>> @instantiate
       ... class Foobar(object):
       ...    def __init__(self):
       ...        print('Init...')
       Init...


       >>> @instantiate('test', context={'x': 1})
       ... class Foobar(object):
       ...    def __init__(self, name, context):
       ...        print('Initializing a Foobar instance with name={name!r} '
       ...              'and context={context!r}'.format(**locals()))
       Initializing a Foobar instance with name='test' and context={'x': 1}

    In all cases, Foobar remains the class, not the instance::

        >>> Foobar  # doctest: +ELLIPSIS
        <class '...Foobar'>
    '''
    target(*args, **kwargs)
    return target


del _decorator


# The following is extracted from the SQLAlchemy project's codebase, merit and
# copyright goes to SQLAlchemy authors::
#
# Copyright (C) 2005-2011 the SQLAlchemy authors and contributors
#
# This module is part of SQLAlchemy and is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php
#
class memoized_property(object):
    """A read-only property that is only evaluated once.

    This is extracted from the SQLAlchemy project's codebase, merit and
    copyright goes to SQLAlchemy authors::

      Copyright (C) 2005-2011 the SQLAlchemy authors and contributors

      This module is part of SQLAlchemy and is released under the MIT License:
      http://www.opensource.org/licenses/mit-license.php

    """
    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        obj.__dict__[self.__name__] = result = self.fget(obj)
        return result


class memoized_instancemethod(object):
    """Decorate a method memoize its return value.

    Best applied to no-arg methods: memoization is not sensitive to
    argument values, and will always return the same value even when
    called with different arguments.

    This is extracted from the SQLAlchemy project's codebase, merit and
    copyright goes to SQLAlchemy authors::

      Copyright (C) 2005-2011 the SQLAlchemy authors and contributors

      This module is part of SQLAlchemy and is released under the MIT License:
      http://www.opensource.org/licenses/mit-license.php

    """
    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self

        def oneshot(*args, **kw):
            result = self.fget(obj, *args, **kw)
            memo = lambda *a, **kw: result
            memo.__name__ = self.__name__
            memo.__doc__ = self.__doc__
            obj.__dict__[self.__name__] = memo
            return result

        oneshot.__name__ = self.__name__
        oneshot.__doc__ = self.__doc__
        return oneshot


def reset_memoized(instance, name):
    instance.__dict__.pop(name, None)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
