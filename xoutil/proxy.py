#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xotl.models.ql.proxy
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
# Created on May 28, 2012

'''
An object proxy utility.

This module allows you to create proxy classes. A proxy instance should have a
`target` attribute that refers to the proxied object. And the proxy class
should have a `behaves` attributes that contains a sequence of new-style
classes that complements the behaviour of wrapped objects.

Refer to the documentation of :py:func:`proxify` for examples.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)


from types import MethodType

from xoutil.context import context
from xoutil.aop import complementor
from xoutil.types import Unset
from xoutil.iterators import first


__docstring_format__ = 'rst'
__author__ = 'manu'


__all__ = (b'SUPPORTED_OPERATIONS', b'proxify')



class UNPROXIFING_CONTEXT(object):
    '''Context to mark a special case in which you don't want to proxy
    to the target object.

    '''



SUPPORTED_UNARY_OPERATIONS = (b'__pos__', b'__abs__', b'__neg__',
                              b'__invert__',)



SUPPORTED_BINARY_LOGICAL_OPERATIONS = (b'__and__', b'__or__', b'__xor__',
                                       b'__lt__', b'__le__', b'__gt__',
                                       b'__ge__', b'__eq__', b'__ne__',

                                       b'__rand__', b'__ror__', b'__rxor__',
                                       b'__iand__', b'__ior__', b'__ixor__',)


SUPPORTED_BINARY_ARITH_OPERATIONS = (b'__add__', b'__sub__', b'__mul__',
                                     b'__div__', b'__mod__', b'__pow__',
                                     b'__truediv__', b'__floordiv__',
                                     b'__lshift__', b'__rshift__',

                                     b'__radd__', b'__rsub__', b'__rmul__',
                                     b'__rdiv__', b'__rmod__', b'__rpow__',
                                     b'__rtruediv__', b'__rfloordiv__',
                                     b'__rlshift__', b'__rrshift__',

                                     b'__iadd__', b'__isub__', b'__imul__',
                                     b'__idiv__', b'__imod__', b'__ipow__',
                                     b'__itruediv__', b'__ifloordiv__',
                                     b'__ilshift__', b'__irshift__',
                                     )


SUPPORTED_BINARY_OPERATIONS = (b'__contains__',)


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
    method.__name__ = method_name
    return method



def build_binary_operator(method_name):
    def method(self, other):
        with context(UNPROXIFING_CONTEXT):
            _super = getattr(self, '_super_%s' % method_name, None)
        if _super:
            return _super(other)
        else:
            return getattr(self, method_name)(other)
    method.__name__ = method_name
    return method



_supported_methods = {mname: build_self_operator(mname)
                        for mname in SUPPORTED_UNARY_OPERATIONS}
_supported_methods.update({mname: build_binary_operator(mname)
                           for mname in SUPPORTED_BINARY_ARITH_OPERATIONS})
_supported_methods.update({mname: build_binary_operator(mname)
                           for mname in SUPPORTED_BINARY_LOGICAL_OPERATIONS})

SupportedOperations = type(b'SupportedOperations', (object,),
                           _supported_methods)



class Proxy(object):
    '''
    A complementor for a "behavior" defined in query expressions or a target \
    object.
    '''
    def __getattribute__(self, attr):
        import types
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
        behaves = get('behaves')
        if not behaves:
            behaves = ()
        valid_wrapper = lambda b: isinstance(getattr(b, attr, None),
                                             types.MethodType)
        wrapper = first(valid_wrapper, (b for b in behaves))
        if wrapper:
            result = getattr(wrapper, attr)
            if getattr(result, 'im_func', None):
                func = result.im_func
                return MethodType(func, self, type(self))
            else:
                return result
        else:
            unset = object()
            result = getattr(target, attr, unset)
            # Treat __eq__ and __ne__ specially.
            if result is unset:
                if attr == '__eq__':
                    return MethodType(lambda s, o: s is o, self, type(self))
                elif attr == '__ne__':
                    return MethodType(lambda s, o: s is not o,
                                      self,
                                      type(self))
                elif attr == '__deepcopy__':
                    return get('__deepcopy__')
                elif attr == 'target':
                    # Allow behaviours to access target attr.
                    return target
                else:
                    return getattr(target, attr)
            else:
                return result



def proxify(cls, *complementors):
    '''
    A decorator to proxify classes with :class:`Proxy`.

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

        >>> r + 1 is 1 + r
        I'm adding <class 'proxy.Proxified'>
        I'm adding <class 'proxy.Proxified'>
        True

    But notice that if neither the proxied object or it's behaviours implement
    a method, an AttributeError exception is raised::

        >>> r < 1                                # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        AttributeError: '...' object has no attribute '__lt__'

    The only exceptions for the above rule are `__eq__` and `__ne__`
    operations, for which we provide a fallback implementation if none is
    provided.

    .. warning: Notice that behaviours classes must not assume that `self` is
                the proxied object but the proxy itself. That's needed for the
                illusion of "added" behaviours to be consistent. If we make
                `self` the proxied object then all the added behaviour we'll be
                lost inside the method call.

                If you need to access the proxied object directly use the
                attribute 'target' of the proxy object (i.e: ``self.target``);
                we treat that attribute specially.

                To the same accord, the fallback implementations of `__eq__`
                and `__ne__` also work at the proxy level. So if we do::

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
                    >>> y == y + 1
                    False

                But be warned! If the proxied object has an attribute `target`
                it will shadow the proxy's::

                    >>> x.target = 'oops'
                    >>> y.target == 'oops'
                    True

                If you need to access any attribute of the proxy and not the
                proxied object without fear of being shadow, use the
                :class:`UNPROXIFING_CONTEXT` context like this::

                    >>> from xoutil.context import context
                    >>> with context(UNPROXIFING_CONTEXT):
                    ...     # access the proxy attributes
                    ...     pass

    '''
    if not complementors:
        complementors = (SupportedOperations, )
    ComplementedProxy = complementor(*complementors)(Proxy)
    return complementor(ComplementedProxy)(cls)
