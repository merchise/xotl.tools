#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.proxy
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Manuel Vázquez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on May 28, 2012

'''An object proxy utility.

This module allows you to create proxy classes. A proxy instance should have a
`target` attribute that refers to the proxied object. And the proxy class
should have a `behaves` attributes that contains a sequence of new-style
classes that complements the behavior of wrapped objects.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

from xoutil import Unset
from xoutil.context import context
from xoutil.aop import complementor

from xoutil.names import strlist as strs
__all__ = strs('SUPPORTED_OPERATIONS', 'proxify')


class UNPROXIFING_CONTEXT(object):
    '''Mark for an :mod:`execution context <xoutil.context>` in which you don't
    want to proxy to the target's attributes. When in this context all
    attribute access will return the proxy's own attributes instead of
    target's ones.

    '''


SUPPORTED_UNARY_OPERATIONS = strs('__pos__', '__abs__', '__neg__',
                                  '__invert__',)


SUPPORTED_BINARY_LOGICAL_OPERATIONS = strs(
    '__and__', '__or__', '__xor__',
    '__lt__', '__le__', '__gt__', '__ge__', '__eq__', '__ne__', '__rand__',
    '__ror__', '__rxor__', '__iand__', '__ior__', '__ixor__'
)


SUPPORTED_BINARY_ARITH_OPERATIONS = strs(
    '__add__', '__sub__', '__mul__',
    '__div__', '__mod__', '__pow__', '__truediv__', '__floordiv__',
    '__lshift__', '__rshift__', '__radd__', '__rsub__', '__rmul__',
    '__rdiv__', '__rmod__', '__rpow__', '__rtruediv__', '__rfloordiv__',
    '__rlshift__', '__rrshift__', '__iadd__', '__isub__', '__imul__',
    '__idiv__', '__imod__', '__ipow__', '__itruediv__', '__ifloordiv__',
    '__ilshift__', '__irshift__'
)


SUPPORTED_BINARY_OPERATIONS = strs('__contains__')


SUPPORTED_OPERATIONS = (SUPPORTED_UNARY_OPERATIONS +
                        SUPPORTED_BINARY_LOGICAL_OPERATIONS +
                        SUPPORTED_BINARY_ARITH_OPERATIONS +
                        SUPPORTED_BINARY_OPERATIONS)


def build_self_operator(method_name):
    def method(self):
        with context(UNPROXIFING_CONTEXT):
            _super = getattr(self, '_super_%s' % method_name, None)
        if _super:
            return _super()
        else:
            return getattr(self, method_name)()
    method.__name__ = str(method_name)
    return method


def build_binary_operator(method_name):
    def method(self, other):
        with context(UNPROXIFING_CONTEXT):
            _super = getattr(self, '_super_%s' % method_name, None)
        if _super:
            return _super(other)
        else:
            return getattr(self, method_name)(other)
    method.__name__ = str(method_name)
    return method


_supported_methods = {str(mname): build_self_operator(mname)
                      for mname in SUPPORTED_UNARY_OPERATIONS}
_supported_methods.update({str(mname): build_binary_operator(mname)
                           for mname in SUPPORTED_BINARY_ARITH_OPERATIONS})
_supported_methods.update({str(mname): build_binary_operator(mname)
                           for mname in SUPPORTED_BINARY_LOGICAL_OPERATIONS})

SupportedOperations = type(str('SupportedOperations'), (object,),
                           _supported_methods)


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


class Proxy(object):
    '''A complementor for a "behavior" defined in query expressions or a target
    object.

    '''
    def __getattribute__(self, attr):
        from functools import partial
        from xoutil.types import is_instancemethod

        def get(name, default=Unset):
            _get = super(type(self), self).__getattribute__
            try:
                return _get(name)
            except AttributeError:
                if default is not Unset:
                    return default
                else:
                    raise

        # TODO: Review why the second condition is necessary.
        if context[UNPROXIFING_CONTEXT] and not attr.startswith('_super_'):
            return get(attr)
        target = get('target')
        behaves = get('behaves', None)
        if not behaves:
            behaves = ()
        valid_wrapper = lambda b: is_instancemethod(b, attr)
        wrapper = next((b for b in behaves if valid_wrapper(b)), None)
        if wrapper:
            result = _mro_getattr(wrapper, attr)
            return partial(result, self)
        else:
            unset = object()
            result = getattr(target, attr, unset)
            # Treat __eq__ and __ne__ specially.
            if result is unset:
                if attr == '__eq__':
                    return partial(lambda s, o: s is o, self)
                elif attr == '__ne__':
                    return partial(lambda s, o: s is not o, self)
                elif attr == '__deepcopy__':
                    return get('__deepcopy__')
                elif attr == 'target':
                    # Allow behaviors to access target attr.
                    return target
                else:
                    raise AttributeError(attr)
            else:
                return result


class unboxed(object):
    '''A small hack to access attributes in an UNPROXIFIED_CONTEXT. Also
    provides support for "updating" a single attribute.

    '''
    def __init__(self, proxy, attr=None):
        self.proxy = proxy
        self.attr = attr

    def __getattribute__(self, attr):
        proxy = super(unboxed, self).__getattribute__('proxy')
        with context(UNPROXIFING_CONTEXT):
            return getattr(proxy, attr)

    def __call__(self, attr):
        '''
        Supports the idiom ``unboxed(proxy)(attr) << value``.
        '''
        get = super(unboxed, self).__getattribute__
        proxy = get('proxy')
        return unboxed(proxy, attr)

    def __lshift__(self, value):
        '''Supports the idiom ``unboxed(x, attrname) << value`` for updating a
        single attribute.

        - If the current value is a list the value get appended.

        - If the current value is a tuple, a new tuple ``current + (value, )``
          is set.

        - If the current value is a dict and value is also a dict, the current
          value is updated with `value` like in: ``current.update(value)``.

        - Otherwise the value is set as if.

        '''
        from collections import Mapping
        get = super(unboxed, self).__getattribute__
        proxy = super(unboxed, self).__getattribute__('proxy')
        attr = get('attr')
        if attr:
            current = getattr(self, attr, Unset)
            if current:
                if isinstance(current, list):
                    current.append(value)
                    value = Unset
                elif isinstance(current, tuple):
                    value = current + (value, )
                elif (isinstance(current, Mapping)
                      and isinstance(value, Mapping)):
                    current.update(value)
                    value = Unset
            if value is not Unset:
                with context(UNPROXIFING_CONTEXT):
                    setattr(proxy, attr, value)
        else:
            pass


def proxify(cls, *complementors):
    '''A decorator to proxify classes with :class:`Proxy`.

    Usage::

        >>> class Foobar(object):
        ...    def hi(self):
        ...        print('Hello from %r' % self)

        >>> class HackedHi(object):
        ...    def hi(self):
        ...        print('Hacked %r' % self)
        ...        return self

        >>> class Addition(object):
        ...    def __add__(self, other):
        ...        print("I'm adding %s" % type(self))
        ...        return self
        ...    __radd__ = __add__

        >>> @proxify
        ... class Proxified(object):
        ...    behaves = [HackedHi, Addition]
        ...    def __init__(self, target):
        ...        self.target = target

        >>> x = Foobar()
        >>> y = Proxified(x)
        >>> r = y.hi()  # doctest: +ELLIPSIS
        Hacked <...>

        >>> r + 1 is 1 + r  # doctest: +ELLIPSIS
        I'm adding <class '...Proxified'>
        I'm adding <class '...Proxified'>
        True

    But notice that if neither the proxied object or it's behaviors implement a
    method, a exception is raised::

        >>> r < 1                                # doctest: +SKIP
        Traceback (most recent call last):
            ...
        AttributeError: ...

    .. note::

       In Python 3 it will be a TypeError.

    The only exceptions for the above rule are `__eq__` and `__ne__`
    operations, for which we provide a fallback implementation if none is
    provided.

    Notice that behaviors classes must not assume that `self` is the proxy
    object instead of the "bare" object itself. That's needed for the illusion
    of "added" behaviors to be consistent.  If we make `self` the bare object
    then all the added behavior we'll be lost inside the method call.

    If you need to access the bare object directly use the attribute `target`
    of the proxy object (i.e: ``self.target``); we treat that attribute
    specially.

    To the same accord, the fallback implementations of `__eq__` and `__ne__`
    also work at the proxy level. So if we do::

        >>> class UnproxifingAddition(object):
        ...    def __add__(self, other):
        ...        return self.target

        >>> @proxify
        ... class Proxified(object):
        ...    behaves = [UnproxifingAddition]
        ...    def __init__(self, target):
        ...        self.target = target

    Now the addition would remove the proxy and the equality test
    will fail::

        >>> x = Foobar()
        >>> y = Proxified(x)
        >>> y is (y + 1)
        False

    .. warning::

       But be warned! If the proxied object has an attribute `target` it will
       shadow the proxy::

            >>> x.target = 'oops'
            >>> y.target == 'oops'
            True

       If you need to access any attribute of the proxy and not the proxied
       object without fear of being shadowed, use the
       :class:`UNPROXIFING_CONTEXT` context like this::

            >>> from xoutil.context import context
            >>> with context(UNPROXIFING_CONTEXT):
            ...     y.target is x
            True

            >>> y.target is x
            False

    '''
    if not complementors:
        complementors = (SupportedOperations,)
    ComplementedProxy = complementor(*complementors)(Proxy)
    return complementor(ComplementedProxy)(cls)


del strs
