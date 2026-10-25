#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Modules utilities."""

from types import ModuleType


class _CustomModuleBase(ModuleType):
    pass


def customize(module, custom_attrs=None, meta=None):
    """Replaces a `module` by a custom one.

    Injects all kwargs into the newly created module's class. This allows to
    have module into which we may have properties or other type of
    descriptors.

    :param module: The module object to customize.

    :param custom_attrs: A dictionary of custom attributes that should be
        injected in the customized module.

        .. versionadded:: 1.4.2 Changes the API, no longer uses the
                          ``**kwargs`` idiom for custom attributes.

    :param meta: The metaclass of the module type. This should be a subclass
                 of `type`. We will actually subclass this metaclass to
                 properly inject `custom_attrs` in our own internal
                 metaclass.

    :returns: A tuple of ``(module, customized, class)`` with the module in
              the first place, `customized` will be True only if the module
              was created (i.e `customize`:func: is idempotent), and the
              third item will be the class of the module (the first item).

    """
    if not isinstance(module, _CustomModuleBase):
        import sys

        meta_base = meta if meta else type

        class CustomModuleType(meta_base):  # type: ignore
            def __new__(cls, name, bases, attrs):
                if custom_attrs:
                    attrs.update(custom_attrs)
                return super().__new__(cls, name, bases, attrs)

        class CustomModule(_CustomModuleBase, metaclass=CustomModuleType):
            def __getattr__(self, attr):
                self.__dict__[attr] = result = getattr(module, attr)
                return result

            def __dir__(self):
                res = set(dir(module))
                if custom_attrs:
                    res |= set(custom_attrs.keys())
                return list(res)

        sys.modules[module.__name__] = result = CustomModule(module.__name__)
        return result, True, CustomModule
    else:
        return module, False, type(module)


def modulemethod(func):
    """Decorator that defines a module-level method.

    Simply a module-level method, will always receive a first argument `self`
    with the module object.

    """
    import sys
    from functools import wraps

    self, _created, cls = customize(sys.modules[func.__module__])

    @wraps(func)
    def inner(*args, **kwargs):
        return func(self, *args, **kwargs)

    setattr(cls, func.__name__, func)
    return inner


def moduleproperty(getter, setter=None, deleter=None, doc=None, base=property):
    """Decorator that creates a module-level property.

    The module of the `getter` is replaced by a custom implementation of the
    module, and the property is injected to the custom module's class.

    The parameter `base` serves the purpose of changing the base for the
    property.  For instance, this allows you to have `memoized_properties
    <xotl.tools.objects.memoized_property>`:func: at the module-level::

        def memoized(self):
            return self
        memoized = moduleproperty(memoized, base=memoized_property)


    .. versionadded:: 1.6.1 Added the `base` parameter.

    """
    import sys

    module = sys.modules[getter.__module__]
    module, _created, cls = customize(module)

    class prop(base):
        if getattr(base, "setter", False):

            def setter(self, func, _name=None):
                result = super().setter(func)
                setattr(cls, _name or func.__name__, result)
                return result

        if getattr(base, "deleter", False):

            def deleter(self, func, _name=None):
                result = super().deleter(func)
                setattr(cls, _name or func.__name__, result)
                return result

    result = prop(getter, doc=doc)
    name = getter.__name__
    setattr(cls, getter.__name__, result)
    set_name = getattr(result, "__set_name__", None)
    if set_name is not None:
        set_name(cls, name)
    if setter:
        result = result.setter(setter, _name=name)
    if deleter:
        result = result.deleter(deleter, _name=name)
    return result
