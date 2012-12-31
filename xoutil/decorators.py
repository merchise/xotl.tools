# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.decorator
#----------------------------------------------------------------------
# Copyright (c) 2009-2011 Medardo Rodríguez
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#



'''Some usefull decorators.'''

# TODO: reconsider all this module


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

import sys

from functools import wraps, partial
from types import FunctionType as function


class AttributeAlias(object):
    '''
    Descriptor to create aliases for object attributes.

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
    '''
    Returns a decorator that sets different attribute values to the decorated
    target (function or class)::

        >>> @settle(name='Name')
        ... class Person(object):
        ...    pass

        >>> Person.name
        'Name'
    '''
    def inner(target):
        for key, value in kwargs.iteritems():
            setattr(target, key, value)
        return target
    return inner


def namer(name, **kwargs):
    '''
    Similar to :func:`settle`, but always consider first argument as *the
    name* (i.e, assigned to `__name__`)::

        >>> @namer('Identity', custom=1)
        ... class I(object):
        ...    pass

        >>> I.__name__
        'Identity'

        >>> I.custom
        1
    '''
    return settle(__name__=name, **kwargs)


def aliases(**kwargs):
    '''
    In a class, create an :class:`AttributeAlias` descriptor for each
    definition as keyword argument (alias=existing_attribute).
    '''
    def inner(target):
        '''
        Direct closure decorator that settle several attribute aliases.
        '''
        assert isinstance(target, type), '"target" must be a class.'
        for alias, field in kwargs.iteritems():
            setattr(target, alias, AttributeAlias(field))
        return target
    return inner



def decorator(caller):
    '''
    Eases the creation of decorators with arguments. Normally a decorator with
    arguments needs three nested functions like this::

        def decorator(*decorator_arguments):
            def real_decorator(target):
                def inner(*args, **kwargs):
                    return target(*args, **kwargs)
                return inner
            return real_decorator

    This decorator reduces the need of the first level by comprising both into
    a single function definition. However it does not removes the need for an
    ``inner`` function::

        >>> @decorator
        ... def plus(target, value):
        ...    from functools import wraps
        ...    @wraps(target)
        ...    def inner(*args):
        ...        return target(*args) + value
        ...    return inner

        >>> @plus(10)
        ... def ident(val):
        ...     return val

        >>> ident(1)
        11

    A decorator with default values for all its arguments (except, of course,
    the first one which is the decorated :param:`target`_) may be invoked
    without parenthesis::

        >>> @decorator
        ... def plus2(func, value=1, missing=2):
        ...    from functools import wraps
        ...    @wraps(func)
        ...    def inner(*args):
        ...        print(missing)
        ...        return func(*args) + value
        ...    return inner

        >>> @plus2
        ... def ident2(val):
        ...     return val

        >>> ident2(10)
        2
        11

    But (if you like) you may place the parenthesis::

        >>> @plus2()
        ... def ident3(val):
        ...     return val

        >>> ident3(10)
        2
        11

    However, this is not for free, you cannot pass a single positional argument
    which type is a function::

        >>> def p():
        ...    print('This is p!!!')

        >>> @plus2(p)
        ... def dummy():
        ...    print('This is dummy')
        Traceback (most recent call last):
            ...
        TypeError: p() takes no arguments (1 given)

    The workaround for this case is to use a keyword argument.
    '''
    @wraps(caller)
    def outer_decorator(*args, **kwargs):
        if len(args) == 1 and not kwargs and isinstance(args[0],
                                                        (function, type)):
            # This tries to solve the case of missing () on the decorator::
            #
            #    @decorator
            #    def somedec(func, *args, **kwargs)
            #        ...
            #
            #    @somedec
            #    def decorated(*args, **kwargs):
            #        pass
            #
            # Notice, however, that this is not general enough, since we try
            # to avoid inspecting the calling frame to see if the () are in
            # place.
            func = args[0]
            # TODO: [med] I don't understand why `**kwargs` if empty
            return partial(caller, func, **kwargs)()
        elif len(args) > 0 or len(kwargs) > 0:
            def _decorator(func):
                return partial(caller, **kwargs)(*((func, ) + args))
            return _decorator
        else:
            return caller
    return outer_decorator


@decorator
def assignment_operator(func, maybe_inline=False):
    '''
    Makes a function that receives a name, and other args to get its first
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
        filename, lineno, funcname, sourcecode_lines, index = inspect.getframeinfo(sys._getframe(1))
        try:
            sourceline = sourcecode_lines[index].strip()
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
            del filename, lineno, funcname, sourcecode_lines, index
    return inner


@decorator
def instantiate(target, *args, **kwargs):
    '''
    Some singleton classes must be instantiated as part of its declaration
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


__all__ = (b'settle',
           b'namer',
           b'aliases',
           b'decorator',
           b'instantiate',
           b'AttributeAlias',
           b'assignment_operator')


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
