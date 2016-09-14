# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# xoutil.inspect
# ----------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved
#
# This file is distributed under the terms of the LICENCE distributed
# with this package.
#
# Created 2014-05-02


'''Extensions to Python's ``inspect`` module.

You may use it as drop-in replacement of ``inspect``.  Although we don't
document all items here.  Refer to :mod:`inspect's <inspect>` documentation.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _absolute_import)


from xoutil.modules import copy_members as _copy_python_module_members
_pm = _copy_python_module_members()

isdatadescriptor = _pm.isdatadescriptor

from xoutil.eight.inspect import (_static_getmro, _check_instance,    # noqa
                                  _check_class, _is_type, _shadowed_dict,
                                  getattr_static)


def get_attr_value(obj, name, *default):
    '''Get a named attribute from an object in a safe way.

    Similar to `getattr` but without triggering dynamic look-up via the
    descriptor protocol, `__getattr__` or `__getattribute__` by using
    `getattr_static`:func:.

    '''
    from xoutil import Undefined
    from xoutil.tools import get_default
    default = get_default(default, Undefined)
    is_type = isinstance(obj, type)
    res = getattr_static(obj, name, Undefined)
    if isdatadescriptor(res):
        try:
            owner = type if is_type else type(obj)
            res = res.__get__(obj, owner)
        except:
            res = Undefined
    if res is Undefined and not is_type:
        cls = type(obj)
        res = getattr_static(cls, name, Undefined)
        if isdatadescriptor(res):
            try:
                res = res.__get__(obj, cls)
            except:
                try:
                    res = res.__get__(cls, type)
                except:
                    res = Undefined
    if res is not Undefined:
        return res
    elif default is not Undefined:
        return default
    else:
        from xoutil.eight import type_name
        msg = "'%s' object has no attribute '%s'"
        raise AttributeError(msg % (type_name(obj), name))


def type_name(obj, affirm=False):
    '''Return the internal name for a type or a callable.

    This function is safe.  If :param obj: is not an instance of a proper type
    then returns the following depending on :param affirm:

    - If False returns None.

    - If True convert a single object to its type before returns the name, but
      if is a tuple, list or set; returns a string with a representation of
      contained types.

    Examples::

      >>> type_name(int)
      'int'

      >>> type_name(0) is None
      True

      >>> type_name(0, affirm=True)
      'int'

      >>> type_name((0, 1.1)) is None
      True

      >>> type_name((0, 1.1), affirm=True)
      '(int, float)'

    '''
    from xoutil.eight import class_types, string_types
    from types import FunctionType, MethodType
    named_types = class_types + (FunctionType, MethodType)
    name = '__name__'
    if isinstance(obj, (staticmethod, classmethod)):
        fn = get_attr_value(obj, '__func__', None)
        if fn:
            obj = fn
    if isinstance(obj, named_types):
        # TODO: Why not use directly `get_attr_value``
        try:
            res = getattr_static(obj, name, None)
            if res:
                if isdatadescriptor(res):
                    res = res.__get__(obj, type)
        except BaseException:
            res = None
        if res is None:
            try:
                res = obj.__name__
            except AttributeError:
                res = None
    else:
        res = None
    if res is None:
        # TODO: Why not use directly `get_attr_value``
        # FIX: Improve and standardize the combination of next code
        res = getattr_static(obj, name, None)
        if res and isdatadescriptor(res):
            res = res.__get__(obj, type(obj))
    if isinstance(res, string_types):
        return res
    elif affirm:
        if isinstance(obj, (tuple, list, set)):
            if isinstance(obj, tuple):
                head, tail = '()'
            elif isinstance(obj, list):
                head, tail = '[]'
            else:
                head, tail = '{}'
            items = ', '.join(type_name(t, affirm) for t in obj)
            return str('%s%s%s' % (head, items, tail))
        else:
            return type_name(type(obj))
    else:
        return None


def _static_issubclass(C, B):
    '''like ``issubclass(C, B) -> bool`` but without using ABCs.

    Return whether class C is a strict subclass (i.e., a derived class) of
    class B.

    When using a tuple as the second argument it's a shortcut for::

      any(_static_issubclass(C, b) for b in B)

    This function returns False instead raising "TypeError: issubclass() arg 2
    must be a class or tuple of classes" if `B` any tuple member) is not
    instance of `type`.

    '''
    mro = _static_getmro(C)
    if isinstance(B, tuple):
        return any(b in mro for b in B)
    else:
        return B in mro


# TODO: Implement a safe version for `attrgetter`

if not getattr(_pm, 'getfullargspec', None):
    from xoutil.ahead.collections import namedtuple
    FullArgSpec = namedtuple(
        'FullArgSpec',
        'args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults,'
        'annotations'
    )

    def getfullargspec(func):
        import inspect
        spec = inspect.getargspec(func)
        return FullArgSpec(
            spec.args, spec.varargs, spec.keywords, spec.defaults,
            None, None, None
        )


# get rid of unused global variables
del _pm, _copy_python_module_members
