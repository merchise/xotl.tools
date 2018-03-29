#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Some useful decorators.'''

# TODO: reconsider all this module


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

import sys

from functools import wraps
from types import FunctionType as function

from xoutil.decorator.meta import decorator


__all__ = ('decorator', 'AttributeAlias', 'settle', 'namer', 'aliases',
           'assignment_operator', 'instantiate',
           'memoized_instancemethod', 'reset_memoized')


class AttributeAlias:
    '''Descriptor to create aliases for object attributes.

    This descriptor is mainly to be used internally by `aliases`:func:
    decorator.

    '''

    def __init__(self, attr_name):
        super().__init__()
        self.attr_name = attr_name

    def __get__(self, instance, owner):
        return getattr(instance or owner, self.attr_name)

    def __set__(self, instance, value):
        setattr(instance, self.attr_name, value)

    def __delete__(self, instance):
        delattr(instance, self.attr_name)


def settle(**kwargs):
    '''Returns a decorator to settle attributes to the decorated target.

    Usage::

       >>> @settle(name='Name')
       ... class Person:
       ...    pass

       >>> Person.name
       'Name'

    '''
    def inner(target):
        for attr in kwargs:
            setattr(target, attr, kwargs[attr])
        return target
    return inner


def namer(name, **kwargs):
    '''Like `settle`:func:, but '__name__' is a required positional argument.

    Usage::

        >>> @namer('Identity', custom=1)
        ... class I:
        ...    pass

        >>> I.__name__
        'Identity'

        >>> I.custom
        1

    '''
    return settle(__name__=name, **kwargs)


def aliases(*names, **kwargs):
    '''In a class, create an `AttributeAlias`:class: descriptor for each
    definition as keyword argument (alias=existing_attribute).

    If "names" are given, then the definition context is looked and are
    assigned to it the same decorator target with all new names::

        >>> @aliases('foo', 'bar')
        ... def foobar(*args):
        ...     'This function is added to its module with two new names.'

    '''
    # FIX: This is not working in methods.
    def inner(target):
        '''Direct closure decorator that settle several attribute aliases.'''
        if kwargs:
            assert isinstance(target, type), '"target" must be a class.'
        if names:
            _locals = sys._getframe(1).f_locals
            for name in names:
                _locals[str(name)] = target
        if kwargs:
            for alias in kwargs:
                field = kwargs[alias]
                setattr(target, alias, AttributeAlias(field))
        return target
    return inner


@decorator
def assignment_operator(func, maybe_inline=False):
    '''Makes a function that receives a name, and other args to get its first
    argument (the name) from an assignment operation, meaning that it if its
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


@decorator
def instantiate(target, *args, **kwargs):
    '''Some singleton classes must be instantiated as part of its declaration
    because they represents singleton objects.

    Every argument, positional or keyword, is passed as such when invoking the
    target. The following two code samples show two cases::

       >>> @instantiate
       ... class Foobar:
       ...    def __init__(self):
       ...        print('Init...')
       Init...


       >>> @instantiate('test', context={'x': 1})
       ... class Foobar:
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


@decorator
def constant_bagger(func, *args, **kwds):
    '''Create a "bag" with constant values.

    Decorated object must be a callable, but the result will be a class
    containing the constant values.

    For example::

      >>> @constant_bagger
      ... def MYBAG():
      ...     return dict(X=1, Y=2)

    It will generate::

      class MYBAG:
          X = 1
          Y = 2

    When called with arguments, these will be used as actual arguments for the
    decorated function::

      >>> @constant_bagger(X=1, Y=2)
      ... def MYBAG(**kwds):
      ...     return kwds

    Constant bags are singletons that can be updated::

      >>> MYBAG(Z=3) is MYBAG
      True

      >>> MYBAG.Z
      3

    '''
    from xoutil.objects import mass_setattr
    wraps = ((a, getattr(func, a, None)) for a in ('__doc__', '__module__'))
    attrs = {a: v for (a, v) in wraps if v}
    attrs.update(__new__=mass_setattr, **func(*args, **kwds))
    return type(func.__name__, (object,), attrs)


@decorator
def singleton(target, *args, **kwargs):
    '''Instantiate a class and assign the instance to the declared symbol.

    Every argument, positional or keyword, is passed as such when invoking the
    target. The following two code samples show two cases::

      >>> @singleton
      ... class foobar:
      ...    def __init__(self):
      ...        self.doc = 'foobar instance'

      >>> foobar.doc
      'foobar instance'

      >>> @singleton('test', context={'x': 1})
      ... class foobar:
      ...     def __init__(self, name, context):
      ...         self.name = name
      ...         self.context = context

      >>> foobar.name, foobar.context
      ('test', {'x': 1})

      >>> isinstance(foobar, type)
      False

    '''
    try:
        from types import ClassType
        class_types = (type, ClassType)
    except ImportError:
        class_types = (type,)
    res = target(*args, **kwargs)
    if isinstance(target, class_types):
        try:
            def __init__(*args, **kwds):
                msg = "'{}' is a singleton, it can be instantiated only once"
                raise TypeError(msg.format(target.__name__))
            target.__init__ = __init__
        except Exception:
            pass
    return res


class memoized_property:
    '''A read-only property that is only evaluated once.

    Deprecated in favor of `xoutil.objects.memoized_property`:class:.

    '''
    def __init__(self, fget, doc=None):
        # XXX: The code was replicated in order to avoid module dependency
        # conflicts
        from warnings import warn
        msg = ('"memoized_property" is now deprecated and it will be '
               'removed. Use the one in "xoutil.objects" module instead.')
        warn(msg, stacklevel=2)
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        obj.__dict__[self.__name__] = result = self.fget(obj)
        return result

    def reset(self, instance):
        instance.__dict__.pop(self.__name__, None)


class memoized_instancemethod:
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
        from warnings import warn
        msg = ('"memoized_instancemethod" is now deprecated and it will be '
               'removed.')
        warn(msg, stacklevel=2)
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
    from warnings import warn
    msg = ('"reset_memoized" is now deprecated and it will be '
           'removed. Use "memoized_property.reset".')
    warn(msg, stacklevel=2)
    instance.__dict__.pop(name, None)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
