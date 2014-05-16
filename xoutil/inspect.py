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
    # Copied from `/usr/lib/python3.3/inspect.py`

    _searchbases = _pm._searchbases
    _sentinel = object()

    def _typeof(obj):
        from types import InstanceType
        return obj.__class__ if isinstance(obj, InstanceType) else type(obj)

    def _static_getmro(klass):
        if isinstance(klass, type):
            return type.__dict__['__mro__'].__get__(klass)
        else:
            res = []
            _searchbases(klass, res)
            return res

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
        except StandardError:
            return False

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
                from types import GetSetDescriptorType as _desc
                if not (type(class_dict) is _desc and
                        class_dict.__name__ == "__dict__" and
                        class_dict.__objclass__ is entry):
                    return class_dict
        return _sentinel

    def _is_descriptor(klass_result):
        _ktype = type(klass_result)
        return (_check_class(_ktype, '__get__') is not _sentinel and
                _check_class(_ktype, '__set__') is not _sentinel)

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
            from types import MemberDescriptorType as _member
            klass = _typeof(obj)
            dict_attr = _shadowed_dict(klass)
            if dict_attr is _sentinel or isinstance(dict_attr, _member):
                instance_result = _check_instance(obj, attr)
        else:
            klass = obj

        klass_result = _check_class(klass, attr)

        if (instance_result is not _sentinel and
                klass_result is not _sentinel and
                _is_descriptor(klass_result)):
            return klass_result
        elif instance_result is not _sentinel:
            return instance_result
        elif klass_result is not _sentinel:
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
            print('>>>', default)
            raise AttributeError(attr)


def get_attr_value(obj, name, *default):
    '''Get a named attribute from an object in a safe way.

    Similar to `getattr` but without triggering dynamic look-up via the
    descriptor protocol, `__getattr__` or `__getattribute__` by using
    ``getattr_static``.

    '''
    from xoutil import Undefined as _undef
    from xoutil.tools import get_default
    default = get_default(default, _undef)
    is_type = isinstance(obj, type)
    res = getattr_static(obj, name, _undef)
    if isdatadescriptor(res):
        try:
            owner = type if is_type else type(obj)
            res = res.__get__(obj, owner)
        except AttributeError:
            res = _undef
    if res is _undef and not is_type:
        cls = type(obj)
        res = getattr_static(cls, name, _undef)
        if isdatadescriptor(res):
            try:
                res = res.__get__(obj, cls)
            except StandardError:
                try:
                    res = res.__get__(cls, type)
                except StandardError:
                    res = _undef
    if res is not _undef:
        return res
    elif default is not _undef:
        return default
    else:
        msg = "'%s' object has no attribute '%s'"
        raise AttributeError(msg % (type(obj).__name__, name))


def type_name(obj):
    '''Return the type or callable internal name.

    This function is saIf not a proper type, try a safe method.

    '''
    from xoutil.six import class_types, string_types
    from types import (FunctionType as function, MethodType as method)
    named_types = class_types + (function, method)
    name = '__name__'
    if isinstance(obj, named_types):
        res = getattr_static(obj, name, None)
        if res and isdatadescriptor(res):
            res = res.__get__(obj, type)
    else:
        res = getattr_static(obj, name, None)
        if res and isdatadescriptor(res):
            res = res.__get__(obj, type(obj))
    return res if isinstance(res, string_types) else None


# TODO: Implement a safe version for `attrgetter`


# get rid of unused global variables
del _pm, _copy_python_module_members
