# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# xoutil.inspect
# ----------------------------------------------------------------------
# Copyright 2014 Merchise Autrement
#
# This file is distributed under the terms of the LICENCE distributed
# with this package.
#
# Created 2014-05-02


'''Extensions to Python's ``inspect`` module.

You may use it as drop-in replacement of ``collections``. Although we don't
document all items here. Refer to :mod:`collections <collections>`
documentation.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)


from xoutil.modules import copy_members as _copy_python_module_members
_pm = _copy_python_module_members()

isdatadescriptor = _pm.isdatadescriptor


try:
    getattr_static = _pm.getattr_static
except AttributeError:
    # This is copied from `/usr/lib/python3.3/inspect.py`
    import types

    _sentinel = object()

    def _static_getmro(klass):
        return type.__dict__['__mro__'].__get__(klass)

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

    def _shadowed_dict(klass):
        dict_attr = type.__dict__["__dict__"]
        for entry in _static_getmro(klass):
            try:
                class_dict = dict_attr.__get__(entry)["__dict__"]
            except KeyError:
                pass
            else:
                if not (type(class_dict) is types.GetSetDescriptorType and
                        class_dict.__name__ == "__dict__" and
                        class_dict.__objclass__ is entry):
                    return class_dict
        return _sentinel

    def getattr_static(obj, attr, default=_sentinel):
        """Retrieve attributes without triggering dynamic lookup via the
           descriptor protocol,  __getattr__ or __getattribute__.

           Note: this function may not be able to retrieve all attributes
           that getattr can fetch (like dynamically created attributes)
           and may find attributes that getattr can't (like descriptors
           that raise AttributeError). It can also return descriptor objects
           instead of instance members in some cases.  See the
           documentation for details.
        """
        instance_result = _sentinel
        if not _is_type(obj):
            klass = type(obj)
            dict_attr = _shadowed_dict(klass)
            if (dict_attr is _sentinel or
                type(dict_attr) is types.MemberDescriptorType):
                instance_result = _check_instance(obj, attr)
        else:
            klass = obj

        klass_result = _check_class(klass, attr)

        if instance_result is not _sentinel and klass_result is not _sentinel:
            if (_check_class(type(klass_result), '__get__') is not _sentinel and
                _check_class(type(klass_result), '__set__') is not _sentinel):
                return klass_result

        if instance_result is not _sentinel:
            return instance_result
        if klass_result is not _sentinel:
            return klass_result

        if obj is klass:
            # for types we check the metaclass too
            for entry in _static_getmro(type(klass)):
                if _shadowed_dict(type(entry)) is _sentinel:
                    try:
                        return entry.__dict__[attr]
                    except KeyError:
                        pass
        if default is not _sentinel:
            return default
        raise AttributeError(attr)


def _getattr(obj, name, *default):
    '''Get a named attribute from an object in a safe way.

    Similar to `getattr` but without triggering dynamic look-up via the
    descriptor protocol, `__getattr__` or `__getattribute__` by using
    ``getattr_static``.

    '''
    _unset = object()
    args = len(default)
    if args in (0, 1):
        is_type = isinstance(obj, type)
        res = getattr_static(obj, name, _unset)
        if isdatadescriptor(res) and not is_type:
            try:
                res = res.__get__(obj, type(obj))
            except AttributeError:
                res = _unset
        if res is _unset and not is_type:
            res = getattr_static(type(obj), name, _unset)
            if isdatadescriptor(res):
                try:
                    res = res.__get__(obj, type(obj))
                except AttributeError:
                    res = _unset
        if res is not _unset:
            return res
        elif args == 1:
            return default[0]
        else:
            msg = "'%s' object has no attribute '%s'"
            raise AttributeError(msg % (type(obj).__name__, name))
    else:
        msg = "'_getattr' expected 2 or 3 arguments, got %s"
        raise TypeError(msg % (args + 2))


# get rid of unused global variables
del _pm, _copy_python_module_members
