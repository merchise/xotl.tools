#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Extensions to Python's ``inspect`` module.

You may use it as drop-in replacement of ``inspect``.  Although we don't
document all items here.  Refer to `inspect's <inspect>`:mod: documentation.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _absolute_import)

from inspect import *    # noqa

from xoutil.deprecation import deprecate_linked
deprecate_linked()
del deprecate_linked


try:
    getfullargspec    # noqa
except NameError:
    from xoutil.future.collections import namedtuple
    FullArgSpec = namedtuple(
        'FullArgSpec',
        'args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults,'
        'annotations')

    def getfullargspec(func):
        import inspect
        spec = inspect.getargspec(func)
        return FullArgSpec(
            spec.args, spec.varargs, spec.keywords, spec.defaults,
            None, None, None)

# Some private imports migrated from 'xoutil.eight.inspect' -->

try:
    from inspect import _sentinel
except ImportError:
    _sentinel = object()

try:
    from inspect import _static_getmro
except ImportError:
    def _safe_search_bases(cls, accum=None):
        # Simulate the "classic class" search order.
        accum = [] if accum is None else accum
        if cls not in accum:
            accum.append(cls)
            for base in cls.__bases__:
                _safe_search_bases(base, accum)
        return accum

    def _static_getmro(klass):
        '''Get a reasonable method resolution order of a class.

        Works well for both old-style and new-style classes.

        '''
        if isinstance(klass, type):
            return type.__dict__['__mro__'].__get__(klass)
        else:
            try:
                from types import ClassType    # old class type
                if isinstance(klass, ClassType):
                    return _safe_search_bases(klass)
            except ImportError:
                # Python 3.1 lacks both _static_getmro and ClassType
                pass
            from xoutil.eight import type_name
            msg = "doesn't apply to '{}' object"
            raise TypeError(msg.format(type_name(klass)))


try:
    from inspect import _check_instance
except ImportError:
    def _check_instance(obj, attr):
        try:
            instance_dict = object.__getattribute__(obj, "__dict__")
        except AttributeError:
            instance_dict = {}
        return dict.get(instance_dict, attr, _sentinel)

try:
    from inspect import _check_class
except ImportError:
    def _check_class(klass, attr):
        for entry in _static_getmro(klass):
            if _shadowed_dict(type(entry)) is _sentinel:
                try:
                    return entry.__dict__[attr]
                except KeyError:
                    pass
        return _sentinel

try:
    from inspect import _is_type
except ImportError:
    def _is_type(obj):
        try:
            _static_getmro(obj)
            return True
        except TypeError:
            return False

try:
    from inspect import _shadowed_dict
except ImportError:
    def _objclass(class_dict, entry):
        try:
            # TODO: Look implementation of `inspect.classify_class_attrs`.
            # Extend this concept to understand the inner type of any class or
            # instance attribute.
            return class_dict.__objclass__ is entry
        except AttributeError:
            # FIX: to avoid error in pypy
            return True

    def _shadowed_dict(klass):
        def dict_get(item):
            if isinstance(item, type):
                return type.__dict__["__dict__"].__get__(item)
            else:
                return {'__dict__': item.__dict__}
        for entry in _static_getmro(klass):
            try:
                class_dict = dict_get(entry)["__dict__"]
            except KeyError:
                pass
            else:
                from xoutil.future.types import GetSetDescriptorType
                if not (type(class_dict) is GetSetDescriptorType and
                        class_dict.__name__ == "__dict__" and
                        _objclass(class_dict, entry)):
                    return class_dict
        return _sentinel

try:
    getattr_static    # noqa
except NameError:
    def _is_descriptor(klass_result):
        _ktype = type(klass_result)
        return (_check_class(_ktype, '__get__') is not _sentinel and
                _check_class(_ktype, '__set__') is not _sentinel)

    def getattr_static(obj, attr, default=_sentinel):
        '''Retrieve attributes without triggering dynamic lookup via the
           descriptor protocol,  __getattr__ or __getattribute__.

           Note: this function may not be able to retrieve all attributes
           that getattr can fetch (like dynamically created attributes)
           and may find attributes that getattr can't (like descriptors
           that raise AttributeError). It can also return descriptor objects
           instead of instance members in some cases.  See the
           documentation for details.
        '''
        from xoutil.eight import typeof
        instance_result = _sentinel
        if not _is_type(obj):
            from xoutil.future.types import MemberDescriptorType as mdt
            klass = typeof(obj)
            dict_attr = _shadowed_dict(klass)
            if dict_attr is _sentinel or type(dict_attr) is mdt:
                instance_result = _check_instance(obj, attr)
        else:
            klass = obj

        klass_result = _check_class(klass, attr)

        ires = instance_result is not _sentinel
        kres = klass_result is not _sentinel
        if ires and kres and _is_descriptor(klass_result):
            return klass_result
        elif ires:
            return instance_result
        elif kres:
            return klass_result
        if obj is klass:
            if isinstance(obj, type):
                # for types we check the metaclass too
                meta_result = _check_class(type(klass), attr)
                if meta_result is not _sentinel:
                    return meta_result
            elif attr == '__name__':
                try:
                    return klass.__name__
                except AttributeError:
                    pass
        if default is not _sentinel:
            return default
        else:
            raise AttributeError(attr)

# <-- end of section migrated from 'xoutil.eight.inspect'


def get_attr_value(obj, name, *default):
    '''Get a named attribute from an object in a safe way.

    Similar to `getattr` but without triggering dynamic look-up via the
    descriptor protocol, `__getattr__` or `__getattribute__` by using
    `getattr_static`:func:.

    '''
    from xoutil.params import check_default, Undefined
    default = check_default()(*default)
    is_type = isinstance(obj, type)
    res = getattr_static(obj, name, Undefined)
    if isdatadescriptor(res):    # noqa
        try:
            owner = type if is_type else type(obj)
            res = res.__get__(obj, owner)
        except Exception:  # TODO: @med Which expections.
            res = Undefined
    if res is Undefined and not is_type:
        cls = type(obj)
        res = getattr_static(cls, name, Undefined)
        if isdatadescriptor(res):    # noqa
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
        from xoutil.eight import type_name
        msg = "'%s' object has no attribute '%s'"
        raise AttributeError(msg % (type_name(obj), name))


def safe_name(obj, affirm=False):
    '''Return the internal name for a type or a callable.

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

    '''
    from xoutil.eight import class_types, string_types
    from types import FunctionType, MethodType
    from types import BuiltinFunctionType, BuiltinMethodType
    named_types = class_types + (FunctionType, MethodType,
                                 BuiltinFunctionType, BuiltinMethodType)
    if isinstance(obj, (staticmethod, classmethod)):
        fn = get_attr_value(obj, '__func__', None)
        if fn:
            obj = fn
    if isinstance(obj, named_types):
        # TODO: Why not use directly `get_attr_value``
        try:
            res = getattr_static(obj, '__name__', None)
            if res:
                if isdatadescriptor(res):    # noqa
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
        res = getattr_static(obj, '__name__', None)
        if res and isdatadescriptor(res):    # noqa
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
            items = ', '.join(safe_name(t, affirm) for t in obj)
            return str('%s%s%s' % (head, items, tail))
        else:
            return safe_name(type(obj))
    else:
        return None


from xoutil.deprecation import deprecated    # noqa

type_name = deprecated(safe_name, removed_in_version='1.8.1')(safe_name)

del deprecated


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
