#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight.inspect
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-11-22

'''Differences between Python 2 and 3 of standard `inspect` module.

See `~xoutil.inspect`:module: for a full replacement.  The standard module
gets useful information from live Python objects.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


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
    from inspect import (_check_instance, _check_class, _is_type,
                         _shadowed_dict, getattr_static)
except ImportError:
    _sentinel = object()

    def _check_instance(obj, attr):
        try:
            instance_dict = object.__getattribute__(obj, "__dict__")
        except AttributeError:
            instance_dict = {}
        return dict.get(instance_dict, attr, _sentinel)

    def _check_class(klass, attr):
        for entry in _static_getmro(klass):
            if _shadowed_dict(type(entry)) is _sentinel:
                try:
                    return entry.__dict__[attr]
                except KeyError:
                    pass
        return _sentinel

    def _is_type(obj):
        try:
            _static_getmro(obj)
            return True
        except TypeError:
            return False

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
        if isinstance(klass, type):
            dict_get = type.__dict__["__dict__"].__get__
        else:
            dict_get = lambda item: {'__dict__': item.__dict__}
        for entry in _static_getmro(klass):
            try:
                class_dict = dict_get(entry)["__dict__"]
            except KeyError:
                pass
            else:
                from xoutil.eight.types import GetSetDescriptorType
                if not (type(class_dict) is GetSetDescriptorType and
                        class_dict.__name__ == "__dict__" and
                        _objclass(class_dict, entry)):
                    return class_dict
        return _sentinel

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
            from xoutil.eight.types import MemberDescriptorType as mdt
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
