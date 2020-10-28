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
from typing import TypeVar
from typing_extensions import Protocol

from types import *  # noqa
import types as _stdlib  # noqa

from xotl.tools.deprecation import deprecated

from xotl.tools.symbols import Unset as _unset
from collections.abc import Mapping


try:
    from types import __all__  # noqa

    __all__ = list(__all__)
except ImportError:
    # Python 3.3 don't implement '__all__' for 'string' module.
    __all__ = [name for name in dir(_stdlib) if not name.startswith("_")]

try:
    NoneType = _stdlib.NoneType  # noqa
except AttributeError:
    try:
        # In PyPy3 'NoneType' is a built-in
        from builtins import NoneType  # noqa
    except ImportError:
        NoneType = type(None)
    __all__.append("NoneType")

try:
    # It is maintained in this module for perhaps using it in `mypy`.
    EllipsisType  # noqa
except NameError:
    EllipsisType = type(Ellipsis)
    __all__.append("EllipsisType")

# Check Jython and PyPy peculiarity
if MemberDescriptorType is GetSetDescriptorType:  # noqa

    class _foo:
        __slots__ = "bar"

    MemberDescriptorType = type(_foo.bar)
    del _foo

FuncTypes = tuple(
    {
        FunctionType,
        MethodType,
        LambdaType,  # noqa
        BuiltinFunctionType,
        BuiltinMethodType,
    }
)  # noqa

func_types = FuncTypes  # Just an alias

from types import _calculate_meta  # noqa


import re

RegexPattern = type(re.compile(""))
del re


def _get_mro_attr(target, name, *default):
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
    from xotl.tools.future.inspect import _static_getmro
    from xotl.tools.params import check_default, Undefined

    # force type
    target = target if isinstance(target, type) else type(target)
    target_mro = _static_getmro(target)
    cls = next((c for c in target_mro if name in c.__dict__), _unset)
    if cls is not _unset:
        return cls.__dict__[name]
    elif check_default()(*default) is not Undefined:
        return default[0]
    else:
        msg = "'{}' type has no attribute '{}'"
        raise AttributeError(msg.format(target, name))


@deprecated(_get_mro_attr)
class mro_dict(Mapping):
    """Utility behaving like a read-only dict of `target` MRO attributes.

    Used internally in this module.

    For example::

      >>> class A:
      ...     x = 12
      ...     y = 34

      >>> class B(A):
      ...     y = 56
      ...     z = 78

      >>> d = mro_dict(B)

      >>> d['x']
      12

      >>> d['y']
      56

      >>> d['z']
      78

    .. deprecated:: 1.8.4

    """

    __slots__ = ("_probes", "_keys")

    def __init__(self, target):
        from xotl.tools.future.inspect import _static_getmro

        type_ = target if isinstance(target, type) else type(target)
        target_mro = _static_getmro(type_)
        self._probes = tuple(c.__dict__ for c in target_mro)
        self._keys = set()

    def __getitem__(self, name):
        from xotl.tools.objects import get_first_of

        result = get_first_of(self._probes, name, default=_unset)
        if result is not _unset:
            return result
        else:
            raise KeyError(name)

    def __iter__(self):
        if not self._keys:
            self._settle_keys()
        return iter(self._keys)

    def __len__(self):
        if not self._keys:
            self._settle_keys()
        return len(self._keys)

    def _settle_keys(self):
        for probe in self._probes:
            for key in probe:
                if key not in self._keys:
                    self._keys.add(key)


@deprecated("None", '"mro_get_value_list" will be removed.')
def mro_get_value_list(cls, name):
    """Return a list with all `cls` class attributes in MRO.

    .. deprecated:: 1.8.4

    """
    return list(mro_get_full_mapping(cls, name).values())


@deprecated("None", '"mro_get_full_mapping" will be removed.')
def mro_get_full_mapping(cls, name):
    """Return a dictionary with all items from `cls` in MRO.

    All values corresponding to `name` must be valid mappings.

    .. deprecated:: 1.8.4

    """
    from xotl.tools.future.inspect import _static_getmro

    cls = cls if isinstance(cls, type) else type(cls)  # force type
    mro = _static_getmro(cls)
    return {t: t.__dict__[name] for t in mro if name in t.__dict__}


@deprecated("``iter(maybe)`` in an exception management block.")
def is_iterable(maybe):
    """Returns True if `maybe` is an iterable object.

    e.g. implements the `__iter__` method::

        >>> is_iterable('all strings are iterable')
        True

        # Numbers are not
        >>> is_iterable(1)
        False

        >>> is_iterable(range(1))
        True

        >>> is_iterable({})
        True

        >>> is_iterable(tuple())
        True

        >>> is_iterable(set())
        True

    .. deprecated:: 1.8.4

    """
    try:
        iter(maybe)
    except TypeError:
        return False
    else:
        return True


_is_collection_replacement = """::
    from xotl.tools.values.simple import collection, nil
    collection(avoid=Mapping)(maybe) is not nil
"""


@deprecated(_is_collection_replacement)
def is_collection(maybe):
    """Test `maybe` to see if it is a tuple, a list, a set or a generator
    function.

    It returns False for dictionaries and strings::

        >>> is_collection('all strings are iterable')
        False

        # Numbers are not
        >>> is_collection(1)
        False

        >>> is_collection(range(1))
        True

        >>> is_collection({})
        False

        >>> is_collection(tuple())
        True

        >>> is_collection(set())
        True

        >>> is_collection(a for a in range(100))
        True

    .. versionchanged:: 1.5.5 UserList are collections.

    .. deprecated:: 1.8.4

    """
    from xotl.tools.values.simple import logic_collection_coerce, nil

    return logic_collection_coerce(maybe) is not nil


@deprecated("``isinstance(maybe, Mapping)``")
def is_mapping(maybe):
    """Test `maybe` to see if it is a valid mapping.

    .. deprecated:: 1.8.4

    """
    return isinstance(maybe, Mapping)


@deprecated('``maybe + ""`` in an exception management block.')
def is_string_like(maybe):
    """Returns True if `maybe` acts like a string.

    .. deprecated:: 1.8.4

    """
    try:
        maybe + ""
    except TypeError:
        return False
    else:
        return True


@deprecated("None", '"is_scalar" will be removed.')
def is_scalar(maybe):
    """Returns if `maybe` is not not an iterable or a string.

    .. deprecated:: 1.8.4

    """
    from collections.abc import Iterable

    return isinstance(maybe, str) or not isinstance(maybe, Iterable)


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


@deprecated("``isinstance(maybe, ModuleType)``")
def is_module(maybe):
    """Returns True if `maybe` is a module.

    .. deprecated:: 1.8.4

    """
    return isinstance(maybe, ModuleType)  # noqa


@deprecated("``all(isinstance(obj, types) for obj in subjects)``")
def are_instances(*args):
    """Return True if every `subject` is an instance of (any) `types`.

    :param subjects: All but last positional arguments.  Are the objects
        required to be instances of `types`.

    :param types: The last positional argument.  Either a single type or a
       sequence of types.  This must meet the conditions on the last
       argument of `isinstance`:func:.

    :returns: True or False.  True if for every `subject`,
       ``isinstance(subject, types)`` is True.  Otherwise, False.

    If no `subjects` are provided return True::

        >>> are_instances(int)
        True

    .. seealso:: The function `no_instances`:func: allows to test for
                 subjects not being instances of types.

    .. deprecated:: 1.8.4

    """
    from xotl.tools.params import check_count

    check_count(args, 1, caller="are_instances")
    *subjects, types = args
    if not subjects:
        isinstance(None, types)  # HACK: always validate `types`.
    return all(isinstance(subject, types) for subject in subjects)


@deprecated("``all(not isinstance(obj, types) for obj in subjects)``")
def no_instances(*args):
    """Return True if every `subject` is **not** an instance of (neither)
    `types`.

    :param subjects: All but last positional arguments.  Are the objects
           required not to be instances of `types`.

    :param types: The last positional argument.  Either a single type or a
           sequence of types.  This must meet the conditions on the last
           argument of `isinstance`:func:.

    :returns: True or False.  True if for every `subject`,
              ``isinstance(subject, types)`` is False.  Otherwise, False.

    If no `subjects` are provided return True::

        >>> no_instances(int)
        True

    .. note:: This is not the same as ``not are_instances(...)``.

       This function requires that *no* subject is an instance of `types`.
       Negating `are_instances`:func: would be True if *any* subject is
       not an instance of `types`.

    .. deprecated:: 1.8.4

    """
    from xotl.tools.params import check_count

    check_count(args, 1, caller="no_instances")
    *subjects, types = args
    if not subjects:
        isinstance(None, types)  # HACK: always validate `types`.
    return all(not isinstance(subject, types) for subject in subjects)


class TypeClass(Protocol):
    pass


# fmt: off
class EqTypeClass(TypeClass, Protocol):  # pragma: no cover
    def __eq__(self, other) -> bool: ...
    def __ne__(self, other) -> bool: ...


class OrdTypeClass(EqTypeClass, Protocol):  # pragma: no cover
    def __le__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __ge__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
# fmt: on

TEq = TypeVar("TEq", bound=EqTypeClass)
TOrd = TypeVar("TOrd", bound=OrdTypeClass)
