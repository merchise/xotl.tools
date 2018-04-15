#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Modules utilities.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from types import ModuleType

# TODO: Implement the concept of module descriptor


def force_module(ref=None):
    '''Load a module from a string or return module if already created.

    If `ref` is not specified (or integer) calling module is assumed looking
    in the stack.

    .. note:: Implementation detail

       Function used to inspect the stack is not guaranteed to exist in all
       implementations of Python.

    '''
    from importlib import import_module
    from xoutil.eight import type_name
    if isinstance(ref, ModuleType):
        return ref
    else:
        if ref is None:
            ref = 1
        if isinstance(ref, int):
            import sys
            frame = sys._getframe(ref)
            try:
                ref = frame.f_globals['__name__']
            finally:
                # As recommended to avoid memory leaks
                del frame
        if not isinstance(ref, str):
            if isinstance(ref, bytes):
                ref = ref.decode()  # Python 3.x
            else:
                try:
                    ref = ref.encode()  # Python 2.x
                except Exception:  # TODO: @med which exceptions expected?
                    msg = "invalid type '{}' for module name '{}'"
                    raise TypeError(msg.format(type_name(ref), ref))
        return import_module(ref)


# TODO: Deprecate this method in favor of ``from <module> import *``
def copy_members(source=None, target=None):
    '''Copy module members from `source` to `target`.

    It's common in `xoutil` package to extend Python modules with the same
    name, for example `xoutil.datetime` has all public members of Python's
    `datetime`.  `copy_members`:func: can be used to copy all members from the
    original module to the extended one.

    :param source: string with source module name or module itself.

        If not given, is assumed as the last module part name of `target`.

    :param target: string with target module name or module itself.

        If not given, target name is looked in the stack of caller module.

    :returns: Source module.
    :rtype: `ModuleType`

    .. warning:: Implementation detail

       Function used to inspect the stack is not guaranteed to exist in all
       implementations of Python.

    '''
    target = force_module(target or 2)
    if source is None:
        source = target.__name__.rsplit('.')[-1]
        if source == target.__name__:
            msg = '"source" and "target" modules must be different.'
            raise ValueError(msg)
    source = force_module(source)
    for attr in dir(source):
        if not attr.startswith('__'):
            setattr(target, attr, getattr(source, attr))
    return source


class _CustomModuleBase(ModuleType):
    pass


def customize(module, custom_attrs=None, meta=None):
    '''Replaces a `module` by a custom one.

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

    '''
    if not isinstance(module, _CustomModuleBase):
        import sys
        meta_base = meta if meta else type

        class CustomModuleType(meta_base):
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
    '''Decorator that defines a module-level method.

    Simply a module-level method, will always receive a first argument `self`
    with the module object.

    '''
    import sys
    from functools import wraps
    self, _created, cls = customize(sys.modules[func.__module__])

    @wraps(func)
    def inner(*args, **kwargs):
        return func(self, *args, **kwargs)

    setattr(cls, func.__name__, func)
    return inner


def moduleproperty(getter, setter=None, deleter=None, doc=None, base=property):
    '''Decorator that creates a module-level property.

    The module of the `getter` is replaced by a custom implementation of the
    module, and the property is injected to the custom module's class.

    The parameter `base` serves the purpose of changing the base for the
    property.  For instance, this allows you to have `memoized_properties
    <xoutil.objects.memoized_property>`:func: at the module-level::

        def memoized(self):
            return self
        memoized = moduleproperty(memoized, base=memoized_property)


    .. versionadded:: 1.6.1 Added the `base` parameter.

    '''
    import sys
    module = sys.modules[getter.__module__]
    module, _created, cls = customize(module)

    class prop(base):
        if getattr(base, 'setter', False):
            def setter(self, func, _name=None):
                result = super().setter(func)
                setattr(cls, _name or func.__name__, result)
                return result

        if getattr(base, 'deleter', False):
            def deleter(self, func, _name=None):
                result = super().deleter(func)
                setattr(cls, _name or func.__name__, result)
                return result

    result = prop(getter, doc=doc)
    name = getter.__name__
    setattr(cls, getter.__name__, result)
    if setter:
        result = result.setter(setter, _name=name)
    if deleter:
        result = result.deleter(deleter, _name=name)
    return result


def get_module_path(module):
    '''Gets the absolute path of a `module`.

    :param module: Either module object or a (dotted) string for the module.

    :returns: The path of the module.

    If the module is a package, returns the directory path (not the path to the
    ``__init__``).

    If `module` is a string and it's not absolute, raises a TypeError.

    '''
    from importlib import import_module
    from xoutil.fs.path import normalize_path
    from xoutil.eight import string_types as strs
    mod = import_module(module) if isinstance(module, strs) else module
    # The __path__ only exists for packages and does not include the
    # __init__.py
    path = mod.__path__[0] if hasattr(mod, '__path__') else mod.__file__
    return normalize_path(path)
