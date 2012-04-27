#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.aop.classical
#----------------------------------------------------------------------
# Copyright (c) 2012 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on Apr 26, 2012

'''
This module provides a very simple and classical way to weave 'aspect classes'
into your own classes.

This "classical" approach is different from the basic approach in
:mod:`xoutil.aop.basic`_ in that this one is meant to apply changes to the
behavior of objects that endure beyond any given context of execution. Once a
class has been weaved, it will behave weaved-like forever.

Also, this implementation does not (can't) weave built-in types.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

import types

from xoutil.functools import wraps, partial
from xoutil.objects import nameof

__docstring_format__ = 'rst'
__author__ = 'manu'


__all__ = (b'StopExceptionChain', 'weave')


class StopExceptionChain(Exception):
    pass


def get_staticattr(obj, name, default=None):
    value = getattr(obj, name, default)
    if isinstance(value, types.MethodType):
        value = value.im_func
    return value

def _build_member(cls, name, target, replacement=None):
    value = getattr(cls, name)
    if isinstance(value, types.MethodType):
        return types.MethodType(replacement or value.im_func,
                                target if value.im_self is cls else None,
                                target if value.im_class is cls else type)
    else:
        return replacement or value

# TODO: Make static --> static, classmethod --> classmethod, and regular methods --> regular.
def _weave_after_method(cls, aspect, method_name,
                        after_method_name='after_{method_name}'):
    '''
    Tries to weave an after method given by :param:`method_name` defined (by
    name convention) in :param:`aspect` into the class :param:`cls`.

    The following two classes define a single method `echo`. The second class
    may raise `ZeroDivisionError`s.

        >>> class GoodClass(object):
        ...    def echo(self, what):
        ...        return what

        >>> class BadClass(object):
        ...    def echo(self, what):
        ...        return (what+1)/what

        >>> good_instance = GoodClass()
        >>> good_instance.echo(0)
        0

        >>> bad_instance = BadClass()
        >>> bad_instance.echo(0)
        Traceback (most recent call last):
            ...
        ZeroDivisionError: integer division or modulo by zero

    Now, let's define a simple class that defines an after_echo and weave the
    previous classes::

        >>> class Logging(object):
        ...    def after_echo(self, method, result, exc_value):
        ...        if not exc_value:
        ...            print('Method {m} returned {result!r}'.format(m=method, result=result))
        ...        else:
        ...            print('When calling method {m}, {exc!r} was raised!'.format(m=method, exc=exc_value))
        ...        return result
        ...
        ...    def after_superecho(self, method, result, exc_value):
        ...        print(type(self))
        ...        return result

        >>> _weave_after_method(GoodClass, Logging, 'echo')
        >>> _weave_after_method(BadClass, Logging, 'echo')

    After weaving every instance (even those that already exists) will behave
    with the new funcionality included::

        >>> good_instance.echo(0)       # doctest: +ELLIPSIS
        Method <...> returned 0
        0

        # You won't see the print result cause the Exception in doctests.
        >>> bad_instance.echo(0)
        Traceback (most recent call last):
            ...
        ZeroDivisionError: integer division or modulo by zero

    You may define another 'aspect' elsewhere an weave it on top::

        >>> class Security(object):
        ...    current_user = 'manu'
        ...    __perms__ = {'manu': {'respond': ['echo'], }, 'anon': {}}
        ...
        ...    @staticmethod
        ...    def after_echo(self, method, result, exc_value):
        ...        if Security.current_user_mayrespond('echo'):
        ...            return result
        ...
        ...    @classmethod
        ...    def current_user_mayrespond(cls, method):
        ...        current_user = cls.get_current_user()
        ...        if current_user in cls.__perms__:
        ...            perms = cls.__perms__.setdefault(current_user, {})
        ...            respond_perms = perms.setdefault('respond', [])
        ...            return method in respond_perms
        ...        else:
        ...            return False
        ...
        ...    @classmethod
        ...    def get_current_user(cls):
        ...        return cls.current_user

        >>> _weave_after_method(GoodClass, Security, 'echo')

        >>> good_instance.echo(0)        # doctest: +ELLIPSIS
        Method <...> returned 0
        0

        # Changing the current user to other than 'manu', has the effect that
        # the Security aspect does not allow to return a response.
        >>> Security.current_user = 'other'
        >>> good_instance.echo(0)                        # doctest: +ELLIPSIS
        Method <...> returned 0
    '''
    method = getattr(cls, method_name)
    after_method_name = after_method_name.format(method_name=method_name)
    after_method = get_staticattr(aspect, after_method_name)

    def inner(self, *args, **kwargs):
        try:
            result = method(self, *args, **kwargs)
        except Exception as error:
            result = None
            exc_value = error
        else:
            exc_value = None
        try:
            result = after_method(self, method, result, exc_value)
            if exc_value:
                raise exc_value
            else:
                return result
        except StopExceptionChain:
            pass

    if method and after_method:
        wrapped = wraps(method)(inner)
        setattr(cls, method_name, wrapped)


def _weave_before_method(cls, aspect, method_name,
                         before_method_name='before_{method_name}'):
    '''
    Tries to weave a before method given by :param:`method_name` defined (by
    name convention) in :param:`aspect` into the class :param:`cls`.

    The following two classes define a single method `echo`. The second class
    may raise `ZeroDivisionError`s.

        >>> class GoodClass(object):
        ...    def echo(self, what):
        ...        return what

        >>> class BadClass(object):
        ...    def echo(self, what):
        ...        return (what+1)/what

        >>> good_instance = GoodClass()
        >>> good_instance.echo(0)
        0

        >>> bad_instance = BadClass()
        >>> bad_instance.echo(0)
        Traceback (most recent call last):
            ...
        ZeroDivisionError: integer division or modulo by zero

    The following class defines a Security aspect that allows the execution of
    methods by user::

        >>> class Security(object):
        ...    current_user = 'manu'
        ...    __perms__ = {'manu': {'execute': ['echo'], }, 'anon': {}}
        ...
        ...    @staticmethod
        ...    def check_execution_permissions(self, method):
        ...        from xoutil.objects import nameof
        ...        if Security.current_user_may_execute(nameof(method)):
        ...            return result
        ...
        ...    @classmethod
        ...    def current_user_may_execute(cls, method):
        ...        current_user = cls.get_current_user()
        ...        if current_user in cls.__perms__:
        ...            perms = cls.__perms__.setdefault(current_user, {})
        ...            respond_perms = perms.setdefault('execute', [])
        ...            if method not in respond_perms:
        ...                raise Exception('Forbidden')
        ...        else:
        ...            raise Exception('Forbidden')
        ...
        ...    @classmethod
        ...    def get_current_user(cls):
        ...        return cls.current_user

    Now let's apply our security aspect::

        >>> _weave_before_method(GoodClass, Security, 'echo', 'check_execution_permissions')
        >>> _weave_before_method(BadClass, Security, 'echo', 'check_execution_permissions')

    Now 'manu' may still execute the 'echo' method for both GoodClass and
    BadClass instances::

        >>> good_instance.echo(1)
        1

        >>> bad_instance.echo(1)
        2

    Other users are not allowed::

        >>> Security.current_user = 'other'
        >>> bad_instance.echo(0) # If allowed it would raise a ZeroDivisionError
        Traceback (most recent call last):
            ...
        Exception: Forbidden


    '''
    method = getattr(cls, method_name)
    before_method_name = before_method_name.format(method_name=method_name)
    before_method = get_staticattr(aspect, before_method_name)

    def inner(self, *args, **kwargs):
        result = before_method(self, method)
        return method(self, *args, **kwargs) or result

    if method and before_method:
        wrapped = wraps(method)(inner)
        setattr(cls, method_name, wrapped)


def _weave_around_method(cls, aspect, method_name,
                          around_method_name='around_{method_name}'):
    '''
    Simply put, replaces a method by another.

        >>> class OriginalClass(object):
        ...    def echo(self, what):
        ...        return what
        ...
        ...    def superecho(self, what):
        ...        return what * what

        >>> class Logger(object):
        ...    def around_any(self, method, *args, **kwargs):
        ...        print('Calling {m} with {args}, {kwargs}'.format(m=method,
        ...                                                         args=args,
        ...                                                         kwargs=kwargs))
        ...        result = method(*args, **kwargs)
        ...        print('... and {result!r} was returned'.format(result=result))
        ...        return self.superecho(result)

        >>> obj = OriginalClass()
        >>> obj.echo(10)
        10

        >>> _weave_around_method(OriginalClass, Logger, 'echo', 'around_any')

        >>> obj.echo(10)            # doctest: +ELLIPSIS
        Calling <...> with (10,), {}
        ... and 10 was returned
        100
    '''
    method = getattr(cls, method_name)
    around_method_name = around_method_name.format(method_name=method_name)
    around_method = get_staticattr(aspect, around_method_name)

    def inner(self, *args, **kwargs):
        bound_method = partial(method, self) # Simulates a bound method
        result = around_method(self, bound_method, *args, **kwargs)
        return result

    if method and around_method:
        wrapped = wraps(method)(inner)
        setattr(cls, method_name, wrapped)

def weave(aspect, target):
    '''
    Weaves an aspect into `target`.

        >>> class Foobar(object):
        ...    def echo(self, what):
        ...        return what

        >>> class Aspect(object):
        ...    def before_echo(self, method):
        ...        print('Echoing....')
        ...
        ...    def after_echo(self, method, result, exc):
        ...        print('...echoed')
        ...        if exc:
        ...            raise StopExceptionChain
        ...        return result
        ...
        ...    def injected(self, who):
        ...        return self.echo(who)

        >>> f = Foobar()
        >>> f.echo(10)
        10

        >>> weave(Aspect, Foobar)
        >>> f.echo(10)
        Echoing....
        ...echoed
        10
    '''
    from xoutil.objects import xdir
    # We need to make sure afters < befores < arounds < others
    key = lambda (n, o): (not callable(getattr(aspect, n, None)),
                          not n.startswith('after_'),
                          not n.startswith('before_'),
                          not n.startswith('around_'),)
    for attr, member in sorted(xdir(aspect, lambda n: not n.startswith('_')),
                               key=key):
        ok = lambda what: callable(member) and attr.startswith(what+'_')
        if ok('after'):
            _weave_after_method(target, aspect, attr[6:])
        elif ok('before'):
            _weave_before_method(target, aspect, attr[7:])
        elif ok('around'):
            _weave_around_method(target, aspect, attr[7:])
        else:
            setattr(target, attr,
                    get_staticattr(aspect, attr))
