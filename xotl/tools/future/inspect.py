#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""Extensions to Python's ``inspect`` module.

You may use it as drop-in replacement of ``inspect``.  Although we don't
document all items here.  Refer to `inspect's <inspect>`:mod: documentation.

"""

from inspect import *  # noqa
from inspect import _check_instance  # noqa
from inspect import _check_class, _is_type, _sentinel, _shadowed_dict, _static_getmro  # noqa


def get_attr_value(obj, name, *default):
    """Get a named attribute from an object in a safe way.

    Similar to `getattr` but without triggering dynamic look-up via the
    descriptor protocol, `__getattr__` or `__getattribute__` by using
    `getattr_static`:func:.

    """
    from xotl.tools.params import Undefined, check_default

    default = check_default()(*default)
    is_type = isinstance(obj, type)
    res = getattr_static(obj, name, Undefined)
    if isdatadescriptor(res):  # noqa
        try:
            owner = type if is_type else type(obj)
            res = res.__get__(obj, owner)
        except Exception:  # TODO: @med Which expections.
            res = Undefined
    if res is Undefined and not is_type:
        cls = type(obj)
        res = getattr_static(cls, name, Undefined)
        if isdatadescriptor(res):  # noqa
            try:
                res = res.__get__(obj, cls)
            except Exception:  # TODO: @med Which?
                try:
                    res = res.__get__(cls, type)
                except Exception:  # TODO: @med Which?
                    res = Undefined
    if res is not Undefined:
        return res
    elif default is not Undefined:
        return default
    else:
        msg = "'%s' object has no attribute '%s'"
        raise AttributeError(msg % (type(obj).__name__, name))


def safe_name(obj, affirm=False):
    """Return the internal name for a type or a callable.

    This function is safe.  If :param obj: is not an instance of a proper type
    then returns the following depending on :param affirm:

    - If ``False`` returns None.

    - If ``True`` convert a single object to its type before returns the name,
      but if is a tuple, list or set; returns a string with a representation
      of contained types.

    Examples::

      >>> safe_name(int)
      'int'

      >>> safe_name(0) is None
      True

      >>> safe_name(0, affirm=True)
      'int'

      >>> safe_name((0, 1.1)) is None
      True

      >>> safe_name((0, 1.1), affirm=True)
      '(int, float)'

    """
    from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType

    named_types = (
        FunctionType,
        MethodType,
        BuiltinFunctionType,
        BuiltinMethodType,
        type,
    )
    if isinstance(obj, (staticmethod, classmethod)):
        fn = get_attr_value(obj, "__func__", None)
        if fn:
            obj = fn
    if isinstance(obj, named_types):
        # TODO: Why not use directly `get_attr_value``
        try:
            res = getattr_static(obj, "__name__", None)
            if res:
                if isdatadescriptor(res):  # noqa
                    res = res.__get__(obj, type)
        except Exception:
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
        res = getattr_static(obj, "__name__", None)
        if res and isdatadescriptor(res):  # noqa
            res = res.__get__(obj, type(obj))
    if isinstance(res, str):
        return res
    elif affirm:
        if isinstance(obj, (tuple, list, set)):
            if isinstance(obj, tuple):
                head, tail = "()"
            elif isinstance(obj, list):
                head, tail = "[]"
            else:
                head, tail = "{}"
            items = ", ".join(safe_name(t, affirm) for t in obj)
            return str("%s%s%s" % (head, items, tail))
        else:
            return safe_name(type(obj))
    else:
        return None


def _static_issubclass(C, B):
    """like ``issubclass(C, B) -> bool`` but without using ABCs.

    Return whether class C is a strict subclass (i.e., a derived class) of
    class B.

    When using a tuple as the second argument it's a shortcut for::

      any(_static_issubclass(C, b) for b in B)

    This function returns False instead raising "TypeError: issubclass() arg 2
    must be a class or tuple of classes" if `B` any tuple member) is not
    instance of `type`.

    """
    mro = _static_getmro(C)
    if isinstance(B, tuple):
        return any(b in mro for b in B)
    else:
        return B in mro
