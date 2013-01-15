#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.decorator.compat
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-01-15

'''Provides decorators related with interoperability Python 2 and Python 3.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

__author__ = "Manuel Vázquez Acosta <mva.led@gmail.com>"
__date__   = "Tue Jan 15 11:38:55 2013"


def metaclass(meta):
    '''Declares a meta class transparently in Python 2 and Python 3.

    Example::

        >>> class Metaclass(type):
        ...     pass

        >>> @metaclass(Metaclass)
        ... class Something(object):
        ...    pass

        >>> type(Something)    # doctest: +ELLIPSIS
        <class '...Metaclass'>

    '''
    class dummy(object):
        pass
    wrapper = type(dummy.__delattr__)

    def is_slotwrapper(maybe):
        return isinstance(maybe, wrapper)

    def is_static(maybe):
        from xoutil.types import Unset
        im_func = getattr(maybe, 'im_func', Unset)
        return im_func is Unset and getattr(maybe, 'func_code', False)

    def is_method(maybe):
        from xoutil.types import Unset
        from xoutil.compat import class_types
        im_self = getattr(maybe, 'im_self', Unset)
        if im_self is not Unset and im_self is None:
            return isinstance(getattr(maybe, 'im_class', None), class_types)

    def is_classmethod(maybe):
        from xoutil.types import Unset
        from xoutil.compat import class_types
        im_self = getattr(maybe, 'im_self', Unset)
        if im_self is not Unset:
            return isinstance(im_self, class_types)

    def extract_attr(cls, name):
        res = getattr(cls, name)
        if is_slotwrapper(res):
            return None
        if is_static(res):
            return staticmethod(res)
        elif is_classmethod(res):
            return classmethod(res.im_func)
        elif is_method(res):
            return res.im_func
        else:
            return res
    def decorator(cls):
        from xoutil.objects import xdir
        attrs = {name: value for name, value in xdir(cls, getter=extract_attr)
                 if name not in ('__class__', '__mro__', '__name__', '__doc__')
                 # XXX [manu]: value might be None if name is a
                 # wrapper_descriptor for things like __delattr__, etc...
                 if value}
        result = meta(cls.__name__, cls.__bases__, attrs)
        result.__doc__ = cls.__doc__
        return result
    return decorator
