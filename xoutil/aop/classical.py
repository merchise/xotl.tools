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
into your own classes/modules.

This "classical" approach is different from the basic approach in
:mod:`xoutil.aop.basic`_ in that this one is meant to apply changes to the
behavior of objects that endure beyond any given context of execution. Once a
class/module has been weaved, it will remain weaved forever.

Also, this implementation does not (can't) weave built-in types.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

import types

from xoutil.types import Unset
from xoutil.functools import wraps, partial


__docstring_format__ = 'rst'
__author__ = 'manu'


__all__ = (b'StopExceptionChain', 'weave')


class StopExceptionChain(Exception):
    pass



def _getattr(obj, attr, default=Unset):
    try:
        if default is not Unset:
            return getattr(obj, attr, default)
        else:
            return getattr(obj, attr)
    except AttributeError:
        raise
    except:
        if default is not Unset:
            return default
        else:
            # TODO: Write a proper message.
            print(obj, attr, repr(default))
            raise AttributeError('Object {o!r} has not attribute {a!r}'.format(o=obj, a=attr))

        
__getattr = partial(_getattr, default=None)


def get_staticattr(obj, name, default=None):
    value = _getattr(obj, name, default)
    if isinstance(value, types.MethodType):
        value = value.im_func
    return value


def bind_method(method, *args, **kwargs):
    if isinstance(method, types.MethodType):
        self = args[0]
        args = args[1:]
        bound_method = types.MethodType(method.im_func, self, type(self))
    else:
        self = None
        bound_method = method
    return self, bound_method, args, kwargs


def build_method(method, inner):
    if isinstance(method, types.MethodType):
        return types.MethodType(inner, method.im_self, method.im_class)
    else:
        # This means is either a simple function inside a module
        # or is staticmethod.
        return inner


def _weave_after_method(target, aspect, method_name,
                        after_method_name='_after_{method_name}'):
    '''
    Tries to weave an after method given by :param:`method_name` defined (by
    name convention) in :param:`aspect` into the class :param:`target`.

    The following two classes define a single method `echo`. The second class
    may raise `ZeroDivisionError`s.

        >>> class GoodClass(object):
        ...    def echo(self, what):
        ...        return what
        ...
        ...    @classmethod
        ...    def superecho(cls, what):
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

    Now, let's define a simple class that defines an _after_echo and weave the
    previous classes::

        >>> class Logging(object):
        ...    def _after_echo(self, method, result, exc_value):
        ...        if not exc_value:
        ...            print('Method {m} returned {result!r}'.format(m=method, result=result))
        ...        else:
        ...            print('When calling method {m}, {exc!r} was raised!'.format(m=method, exc=exc_value))
        ...        return result
        ...
        ...    def _after_superecho(self, method, result, exc_value):
        ...        print(type(self))
        ...        return result

        >>> _weave_after_method(GoodClass, Logging, 'echo')
        >>> _weave_after_method(GoodClass, Logging, 'superecho')
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

        # Class methods remains classmethods
        >>> good_instance.superecho(0)
        <type 'type'>
        0

    You may define another 'aspect' elsewhere an weave it on top::

        >>> class Security(object):
        ...    current_user = 'manu'
        ...    __perms__ = {'manu': {'respond': ['echo'], }, 'anon': {}}
        ...
        ...    @staticmethod
        ...    def _after_echo(self, method, result, exc_value):
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
    method = _getattr(target, method_name, None)
    after_method_name = after_method_name.format(method_name=method_name)
    after_method = get_staticattr(aspect, after_method_name, None)

    if method and after_method:
        @wraps(method)
        def inner(*args, **kwargs):
            self, bound_method, args, kwargs = bind_method(method, *args, **kwargs)
            try:
                # We don't need to pass self to a bound method
                result = bound_method(*args, **kwargs)
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

        wrapper = build_method(method, inner)
        setattr(target, method_name, wrapper)


def _weave_before_method(target, aspect, method_name,
                         before_method_name='_before_{method_name}'):
    '''
    Tries to weave a before method given by :param:`method_name` defined (by
    name convention) in :param:`aspect` into the class :param:`target`.

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
    method = _getattr(target, method_name, None)
    before_method_name = before_method_name.format(method_name=method_name)
    before_method = get_staticattr(aspect, before_method_name, None)

    @wraps(method)
    def inner(*args, **kwargs):
        self, bound_method, args, kwargs = bind_method(method, *args, **kwargs)
        result = before_method(self, method)
        # We don't need to pass self to a bound method
        return bound_method(*args, **kwargs) or result

    if method and before_method:
        wrapped = build_method(method, inner)
        setattr(target, method_name, wrapped)


def _weave_around_method(cls, aspect, method_name,
                          around_method_name='_around_{method_name}'):
    '''
    Simply put, replaces a method by another.

        >>> class OriginalClass(object):
        ...    def echo(self, what):
        ...        return what
        ...
        ...    def superecho(self, what):
        ...        return what * what

        >>> class Logger(object):
        ...    def _around_any(self, method, *args, **kwargs):
        ...        print('Calling {m} with {args}, {kwargs}'.format(m=method,
        ...                                                         args=args,
        ...                                                         kwargs=kwargs))
        ...        result = method(*args, **kwargs)
        ...        print('... and {result!r} was returned'.format(result=result))
        ...        return self.superecho(result)

        >>> obj = OriginalClass()
        >>> obj.echo(10)
        10

        >>> _weave_around_method(OriginalClass, Logger, 'echo', '_around_any')

        >>> obj.echo(10)            # doctest: +ELLIPSIS
        Calling <...> with (10,), {}
        ... and 10 was returned
        100
    '''
    method = _getattr(cls, method_name, None)
    around_method_name = around_method_name.format(method_name=method_name)
    around_method = get_staticattr(aspect, around_method_name, None)

    @wraps(method)
    def inner(*args, **kwargs):
        self, bound_method, args, kwargs = bind_method(method, *args, **kwargs)
        result = around_method(self, bound_method, *args, **kwargs)
        return result

    if method and around_method:
        wrapped = build_method(method, inner)
        setattr(cls, method_name, wrapped)



_method_name = lambda attr: attr[attr.find('_') + 1:]
_not = lambda func: (lambda *args, **kwargs: not func(*args, **kwargs))
_and = lambda *preds: (lambda *args, **kwargs: all(p(*args, **kwargs) for p in preds))
_or = lambda *preds: (lambda *args, **kwargs: any(p(*args, **kwargs) for p in preds))

_private = lambda attr: attr.startswith('_')
_aspect_method = lambda attr: any(attr.startswith(prefix) and attr != prefix
                                    for prefix in ('_after_',
                                                   '_before_',
                                                   '_around_'))
_public = _not(_private)


def weave(aspect, target):
    '''
    Weaves an aspect into `target`. The weaving takes places like this:

    - First every public attribute from :param:`aspect` that is not an after
      method, before method, or around method is injected into :param:`target`.

    - Then, we weaving any after, before and arounds methods into
      :param:`target` if there's a matching method.

    - Lastly, if there's a `_after_` method in :param:`aspect` it is weaved into
      all methods of :param:`target` (even those which were injected and weaved
      previously).

      The same is done for `_before_` and `_around_`.

    Since the introduction :mod:`xoutil.aop.meta` this method might look for a
    `_before_weave` or a `_around_weave` method in :param:`aspect`; which allow
    aspects to hook this method.
    '''
    from xoutil.objects import fdir
    # Inject all public, non-aspect method
    for attr in fdir(aspect, _and(_public, _not(_aspect_method)), getattr=__getattr):
        setattr(target, attr, get_staticattr(aspect, attr))
    # Weave aspect methods but keep an order scheme:
    #     afters < before < around
    key = lambda n: (not callable(_getattr(aspect, n, None)),
                     not n.startswith('_after_'),
                     not n.startswith('_before_'),
                     not n.startswith('_around_'),)
    for attr in sorted(fdir(aspect, _aspect_method, callable, getattr=__getattr),
                       key=key):
        ok = lambda what: attr.startswith(what + '_')
        if ok('after'):
            _weave_after_method(target, aspect, _method_name(attr))
        elif ok('before'):
            _weave_before_method(target, aspect, _method_name(attr))
        elif ok('around'):
            _weave_around_method(target, aspect, _method_name(attr))
    aspect_dict = dir(aspect)
    if '_after_' in aspect_dict:
        for attr in fdir(target, value_filter=callable, getattr=__getattr):
            _weave_after_method(target, aspect, attr, '_after_')
    if '_before_' in aspect_dict:
        for attr in fdir(target, value_filter=callable, getattr=__getattr):
            _weave_before_method(target, aspect, attr, '_before_')
    if '_around_' in aspect_dict:
        for attr in fdir(target, value_filter=callable, getattr=__getattr):
            _weave_around_method(target, aspect, attr, '_around_')
