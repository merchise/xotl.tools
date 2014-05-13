#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.aop.classical
#----------------------------------------------------------------------
# Copyright (c) 2012, 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# Author: Manuel Vázquez Acosta
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Apr 26, 2012

'''This module provides a very simple and classical way to weave 'aspect
classes' into your own classes/modules.

This "classical" approach is different from the basic approach in
:mod:`~xoutil.aop.basic` in that this one is meant to apply changes to the
behavior of objects that endure beyond any given context of execution. Once a
class/module has been weaved, it will remain weaved forever.

Also, this implementation does not (can't) weave built-in types.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


import types
from functools import wraps as _wraps, partial

from xoutil import Unset
from xoutil.six import PY3 as _py3, callable
from xoutil.deprecation import deprecated as _deprecated
from xoutil.names import strlist as strs

if _py3:
    from inspect import getfullargspec as _getfullargspec
else:
    from inspect import getargspec as _getfullargspec
del _py3

__all__ = strs('weave', 'StopExceptionChain')
del strs


def wraps(target):
    '''Hacks functools.wraps to bypass wrapper descriptors (for __repr__,
    etc.)

    '''
    from xoutil.types import is_slotwrapper
    if not is_slotwrapper(target):
        return _wraps(target)
    else:
        return target


class StopExceptionChain(Exception):
    pass


def _filter_args_byspec(method, *args, **kwargs):
    from xoutil.objects import get_first_of
    spec = _getfullargspec(method)
    if not spec.varargs:
        args = ()
    # XXX: [manu] In Python 3.2, the FullArgsSpec named tuple does not have a
    # keywords attribute, but a varkw and both kwonlyargs and
    # kwonlydefaults.
    #
    # Since spec is a named tuple, it must be enclosed in an outer tuple.
    keywords = get_first_of((spec, ), 'keywords', 'varkw')
    if not keywords:
        kwargs = {}
    return (args, kwargs)


# TODO: [manu] This is repeated in "xoutil.proxy"
def _mro_getattr(obj, attr, default=Unset):
    '''Gets the attr from obj's MRO'''
    from xoutil.types import mro_dict
    unset = object()
    res = mro_dict(obj).get(attr, unset)
    if res is unset:
        if default is Unset:
            raise AttributeError(attr)
        else:
            return default
    else:
        return res
_mro_getattrdef = partial(_mro_getattr, default=None)


def get_staticattr(obj, attr, default=None):
    '''Gets the attribute `attr` by using `getattr`.'''
    value = getattr(obj, attr, default)
    # XXX: In Python 2.7, this may return a bound/unbound method, with a
    #      im_func.
    value = getattr(value, 'im_func', value)
    return value


def bind_method(method, *args, **kwargs):
    '''Returns the method to be called already bound to self if needed'''
    from xoutil.types import is_instancemethod, is_classmethod, is_staticmethod
    if args and is_instancemethod(method):
        self = args[0]
        args = args[1:]
        bound_method = _wraps(method)(lambda *args, **kwargs: method(self,
                                                                    *args,
                                                                    **kwargs))
    elif args and is_classmethod(method):
        self = args[0]
        args = args[1:]
        bound_method = _wraps(method.__func__)(lambda *a, **kw:
                                               method.__func__(self,
                                                               *a,
                                                               **kw))
    elif is_staticmethod(method):
        self = None
        bound_method = method.__func__
    else:
        self = None
        bound_method = method
    return self, bound_method, args, kwargs


def build_method(method, inner):
    from xoutil.types import is_staticmethod, is_classmethod
    if is_staticmethod(method):
        return staticmethod(inner)
    elif is_classmethod(method):
        return classmethod(inner)
    else:
        return inner


def _weave_after_method(target, aspect, method_name,
                        after_method_name='_after_{method_name}'):
    '''Weaves an after method given by `method_name` defined (by name
    convention) in `aspect` into the class `target`.

    The following two classes define a single method `echo`. The second class
    may raise `ZeroDivisionError`s::

        >>> class GoodClass(object):
        ...    def echo(self, what):
        ...        return what
        ...
        ...    @classmethod
        ...    def superecho(cls, what):
        ...        return what

        >>> class BadClass(object):
        ...    def echo(self, what):
        ...        return (what+1)//what

        >>> good_instance = GoodClass()
        >>> good_instance.echo(0)
        0

        >>> bad_instance = BadClass()
        >>> bad_instance.echo(0)               # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ZeroDivisionError: ...

    Now, let's define a simple class that defines an _after_echo and weave the
    previous classes::

        >>> class Logging(object):
        ...    def _after_echo(self, method, result, exc_value):
        ...        if not exc_value:
        ...            print('Method {m} returned {result!r}'.
        ...                  format(m=method, result=result))
        ...        else:
        ...            print('When calling method {m}, {exc!r} was raised!'.
        ...                  format(m=method, exc=exc_value))
        ...        return result
        ...
        ...    def _after_superecho(self, method, result, exc_value):
        ...        print(type(self))
        ...        return result

        >>> _weave_after_method(GoodClass, Logging, 'echo')
        >>> _weave_after_method(GoodClass, Logging, 'superecho')
        >>> _weave_after_method(BadClass, Logging, 'echo')

    After weaving every instance (even those that already exists) will behave
    with the new functionality included::

        >>> good_instance.echo(0)       # doctest: +ELLIPSIS
        Method <...> returned 0
        0

        # You won't see the print result cause the Exception in doctests.
        >>> bad_instance.echo(0)        # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ZeroDivisionError: ...

        # Class methods remains classmethods
        >>> good_instance.superecho(0)  # doctest: +ELLIPSIS
        <...'type'>
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
    from xoutil.types import is_module
    if is_module(target):
        method = getattr(target, method_name, None)
    else:
        method = _mro_getattr(target, method_name, None)
    after_method_name = after_method_name.format(method_name=method_name)
    after_method = get_staticattr(aspect, after_method_name, None)

    if method and after_method:
        @wraps(getattr(method, '__func__', method))
        def inner(*args, **kwargs):
            self, bound_method, args, kwargs = bind_method(method,
                                                           *args, **kwargs)
            try:
                # We don't need to pass self to a bound method
                result = bound_method(*args, **kwargs)
            except Exception as error:
                result = None
                exc_value = error
            else:
                exc_value = None
            try:
                after_args, after_kw = _filter_args_byspec(after_method,
                                                           *args, **kwargs)
                result = after_method(self, method, result, exc_value,
                                      *after_args, **after_kw)
                if exc_value:
                    raise exc_value
                else:
                    return result
            except StopExceptionChain:
                pass

        wrapper = build_method(method, inner)
        if isinstance(target, types.ModuleType):
            import sys
            from xoutil.names import nameof
            target = sys.modules[nameof(target, inner=True)]
        setattr(target, method_name, wrapper)


def _weave_before_method(target, aspect, method_name,
                         before_method_name='_before_{method_name}'):
    '''Tries to weave a before method given by `method_name` defined (by name
    convention) in `aspect` into the class `target`.

    The following two classes define a single method `echo`. The second class
    may raise `ZeroDivisionError`s::

        >>> class GoodClass(object):
        ...    def echo(self, what):
        ...        return what

        >>> class BadClass(object):
        ...    def echo(self, what):
        ...        return (what+1)//what

        >>> good_instance = GoodClass()
        >>> good_instance.echo(0)
        0

        >>> bad_instance = BadClass()
        >>> bad_instance.echo(0)    # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ZeroDivisionError: ...

    The following class defines a Security aspect that allows the execution of
    methods by user::

        >>> class Security(object):
        ...    current_user = 'manu'
        ...    __perms__ = {'manu': {'execute': ['echo'], }, 'anon': {}}
        ...
        ...    @staticmethod
        ...    def check_execution_permissions(self, method):
        ...        from xoutil.names import nameof
        ...        methodname = nameof(method, inner=True)
        ...        if Security.current_user_may_execute(methodname):
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

        >>> _weave_before_method(GoodClass, Security,
        ...                      'echo', 'check_execution_permissions')
        >>> _weave_before_method(BadClass, Security,
        ...                      'echo', 'check_execution_permissions')

    Now 'manu' may still execute the 'echo' method for both GoodClass and
    BadClass instances::

        >>> good_instance.echo(1)
        1

        >>> bad_instance.echo(1)
        2

    Other users are not allowed::

        >>> Security.current_user = 'other'
        >>> bad_instance.echo(0) # If allowed it'd raise a ZeroDivisionError
        Traceback (most recent call last):
            ...
        Exception: Forbidden

    '''
    method = _mro_getattr(target, method_name, None)
    before_method_name = before_method_name.format(method_name=method_name)
    before_method = get_staticattr(aspect, before_method_name, None)

    @wraps(method)
    def inner(*args, **kwargs):
        self, bound_method, args, kwargs = bind_method(method, *args, **kwargs)
        before_args, before_kwargs = _filter_args_byspec(before_method,
                                                         *args,
                                                         **kwargs)
        result = before_method(self, method, *before_args, **before_kwargs)
        # We don't need to pass self to a bound method
        return bound_method(*args, **kwargs) or result

    if method and before_method:
        wrapped = build_method(method, inner)
        setattr(target, method_name, wrapped)


def _weave_around_method(cls, aspect, method_name,
                          around_method_name='_around_{method_name}'):
    '''Simply put, replaces a method by another::

        >>> class OriginalClass(object):
        ...    def echo(self, what):
        ...        return what
        ...
        ...    def superecho(self, what):
        ...        return what * what

        >>> class Logger(object):
        ...    def _around_any(self, method, *args, **kwargs):
        ...        print('Calling {m} with {args}, {kwargs}'.
        ...              format(m=method, args=args, kwargs=kwargs))
        ...        result = method(*args, **kwargs)
        ...        print('... and {result!r} was returned'.
        ...              format(result=result))
        ...        return self.superecho(result)

        >>> obj = OriginalClass()
        >>> obj.echo(10)
        10

        >>> _weave_around_method(OriginalClass, Logger, 'echo', '_around_any')

        >>> obj.echo(10)            # doctest: +ELLIPSIS
        Calling ... with (10,), {}
        ... and 10 was returned
        100

    '''
    method = _mro_getattr(cls, method_name, None)
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


_method_name = lambda attr: attr[attr[1:].find('_') + 2:]
_not = lambda func: (lambda *a, **kw: not func(*a, **kw))
_and = lambda *preds: (lambda *a, **kw: all(p(*a, **kw) for p in preds))
_or = lambda *preds: (lambda *a, **kw: any(p(*a, **kw) for p in preds))

_private = lambda attr: attr.startswith('_')
_aspect_method = lambda attr: any(attr.startswith(prefix) and attr != prefix
                                    for prefix in ('_after_',
                                                   '_before_',
                                                   '_around_'))
#_public = _not(_private)
_public = lambda attr: not attr.startswith('_')


@_deprecated('None', msg="This entire module is deprecated and will be "
             "removed.", removed_in_version='1.6.0')
def weave(aspect, target, *ignored):
    '''Weaves an aspect into `target`. The weaving involves:

    - First every public attribute from `aspect` that is not an after method,
      before method, or around method is injected into `target`.

    - Then, we weave any after, before and around methods into `target` if
      there's a matching method.

    - Lastly, if there's a `_after_` method in `aspect` it is weaved into all
      *public* methods of `target` (even those which were injected and weaved
      previously).

      The same is done for `_before_` and `_around_`.

    Since the introduction :mod:`xoutil.aop.extended` this method might look
    for a `_before_weave` or a `_around_weave` method in `aspect`; which allow
    aspects to hook this method.

    :param aspect: The aspect class.
    :param target: The class to be weaved

    :param ignored: Any attribute name passed in `ignored` is not weaved.

                    .. versionadded:: 1.1.6

    '''
    from xoutil.objects import fdir
    from xoutil.iterators import flatten
    ignored = tuple(flatten(ignored))
    # Inject all public, non-aspect method
    for attr in fdir(aspect, _and(_public, _not(_aspect_method)),
                     getter=_mro_getattrdef):
        setattr(target, attr, get_staticattr(aspect, attr))
    # Weave aspect methods but keep an order scheme:
    #     afters < before < around
    key = lambda n: (not callable(_mro_getattr(aspect, n, None)),
                     not n.startswith('_after_'),
                     not n.startswith('_before_'),
                     not n.startswith('_around_'),)
    for attr in sorted(fdir(aspect, _aspect_method, callable,
                            getter=_mro_getattrdef),
                       key=key):
        ok = lambda what: (attr.startswith('_' + what + '_') and
                           attr not in ignored)
        if ok('after'):
            _weave_after_method(target, aspect, _method_name(attr))
        elif ok('before'):
            _weave_before_method(target, aspect, _method_name(attr))
        elif ok('around'):
            _weave_around_method(target, aspect, _method_name(attr))
    aspect_dict = dir(aspect)
    method = lambda maybe: isinstance(maybe, (types.MethodType,
                                              types.FunctionType))
    if '_after_' in aspect_dict:
        for attr in fdir(target, attr_filter=_public, value_filter=method,
                         getter=_mro_getattrdef):
            _weave_after_method(target, aspect, attr, '_after_')
    if '_before_' in aspect_dict:
        for attr in fdir(target, attr_filter=_public, value_filter=method,
                         getter=_mro_getattrdef):
            _weave_before_method(target, aspect, attr, '_before_')
    if '_around_' in aspect_dict:
        for attr in fdir(target, attr_filter=_public, value_filter=method,
                         getter=_mro_getattrdef):
            _weave_around_method(target, aspect, attr, '_around_')


del _deprecated
