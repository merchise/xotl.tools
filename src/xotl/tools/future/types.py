#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""Extends the standard `types` module.

Standard module defines names for all type symbols known in the standard
interpreter.

This modules mirrors all the functions (and, in general, objects) from the
standard library module `types`:mod:; but it also includes several new types
and type-related functions.

In Jython and PyPy, `MemberDescriptorType` is identical to
`GetSetDescriptorType`; to mantain compatibility in some `xotl.tools` code,
they are differentiated in this module.

"""

import re
from inspect import _static_getmro  # type: ignore
from types import (
    BuiltinFunctionType,
    BuiltinMethodType,
    FunctionType,
    GetSetDescriptorType,
    LambdaType,
    MemberDescriptorType,
    MethodType,
)
from typing import TypeVar

from typing_extensions import Protocol
from xotl.tools.params import Undefined
from xotl.tools.symbols import Unset as _unset

try:
    from types import NoneType  # type: ignore
except ImportError:
    try:
        # In PyPy3 'NoneType' is a built-in
        from builtins import NoneType  # type: ignore
    except ImportError:
        NoneType = type(None)  # type: ignore

EllipsisType = type(Ellipsis)


# Check Jython and PyPy peculiarity
if MemberDescriptorType is GetSetDescriptorType:

    class _foo:
        __slots__ = "bar"

    MemberDescriptorType = type(_foo.bar)  # type: ignore
    del _foo


FuncTypes = tuple({
    FunctionType,
    MethodType,
    LambdaType,
    BuiltinFunctionType,
    BuiltinMethodType,
})

func_types = FuncTypes  # Just an alias


RegexPattern = type(re.compile(""))


def _get_mro_attr(target, name, default=Undefined, /):
    """Get a named attribute from a type.

    Similar to `getattr` but looking in the MRO dictionaries for the type.
    Used internally in this module.

    For example::

      >>> class A(SimpleNamespace):
      ...     x = 12
      ...     y = 34

      >>> class B(A):
      ...     y = 56

      >>> b = B(x=1, y=2)

      >>> _get_mro_attr(b, 'x')
      12

      >>> _get_mro_attr(b, 'y')
      56

    """
    # force type
    target = target if isinstance(target, type) else type(target)
    target_mro = _static_getmro(target)
    cls = next((c for c in target_mro if name in c.__dict__), _unset)
    if cls is not _unset:
        return cls.__dict__[name]
    elif default is not Undefined:
        return default
    else:
        msg = "'{}' type has no attribute '{}'"
        raise AttributeError(msg.format(target, name))


def is_staticmethod(cls, name):
    """Returns true if a `method` is a static method.

    :param cls: The class or object that holds the method.

    :param name: The name of the method.

    When a static-method is declared, you can not test that condition using
    the traditional way::

      >>> class Foo:
      ...     @staticmethod
      ...     def bar():
      ...         pass

      >>> isinstance(Foo.bar, staticmethod)
      False

    Using this function::

      >>> is_staticmethod(Foo, 'bar')
      True

    """
    desc = _get_mro_attr(cls, name)
    return isinstance(desc, staticmethod)


def is_classmethod(cls, name):
    """Returns if a `method` is a class method.

    :param cls: The class or object that holds the method.

    :param name: The name of the method.

    When a class-method is declared, you can not test that condition using the
    traditional way::

      >>> class Foo:
      ...     @classmethod
      ...     def bar(cls):
      ...         pass

      >>> isinstance(Foo.bar, classmethod)
      False

    Using this function::

      >>> is_classmethod(Foo, 'bar')
      True

    """
    desc = _get_mro_attr(cls, name)
    return isinstance(desc, classmethod)


def is_instancemethod(cls, name):
    """Returns if a `method` is neither a static nor a class method.

    :param cls: The class or object that holds the method.

    :param name: The name of the method.

    To find out if a method is "normal", ``isinstance(obj.method,
    MethodType)`` can't be used::

      >>> class Foobar:
      ...     @classmethod
      ...     def cm(cls):
      ...         pass
      ...     def im(self):
      ...         pass

      >>> isinstance(Foobar.cm, MethodType)
      True

    Using this function::

      >>> is_instancemethod(Foobar, 'im')
      True

      >>> is_instancemethod(Foobar, 'cm')
      False

    """
    desc = _get_mro_attr(cls, name)
    return isinstance(desc, FunctionType)  # noqa


class TypeClass(Protocol):
    pass


# fmt: off
class EqTypeClass(TypeClass, Protocol):  # pragma: no cover
    def __eq__(self, other) -> bool: ...  # noqa
    def __ne__(self, other) -> bool: ...  # noqa


class OrdTypeClass(EqTypeClass, Protocol):  # pragma: no cover
    def __le__(self, other) -> bool: ...  # noqa
    def __lt__(self, other) -> bool: ...  # noqa
    def __ge__(self, other) -> bool: ...  # noqa
    def __gt__(self, other) -> bool: ...  # noqa
# fmt: on


TEq = TypeVar("TEq", bound=EqTypeClass)
TOrd = TypeVar("TOrd", bound=OrdTypeClass)


__all__ = (
    "EllipsisType",
    "EqTypeClass",
    "FuncTypes",
    "MemberDescriptorType",
    "NoneType",
    "OrdTypeClass",
    "RegexPattern",
    "TEq",
    "TOrd",
    "TypeClass",
    "func_types",
    "is_classmethod",
    "is_instancemethod",
    "is_staticmethod",
)
