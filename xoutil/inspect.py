# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# xoutil.inspect
# ----------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
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
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)


from xoutil.modules import copy_members as _copy_python_module_members
_pm = _copy_python_module_members()
types = _pm.types

isdatadescriptor = _pm.isdatadescriptor

# TODO: Rename all use of `StandardException`
from xoutil.eight.exceptions import StandardError as StandardException

try:
    getattr_static = _pm.getattr_static
except AttributeError:
    # Copied from `/usr/lib/python3.3/inspect.py`
    # TODO: Maybe all these function must be moved to eight
    from xoutil.eight import typeof as _typeof
    _sentinel = object()

    def _safe_search_bases(cls, accum):
        # Simulate the "classic class" search order.
        if cls in accum:
            return
        else:

            accum.append(cls)
            for base in cls.__bases__:
                _safe_search_bases(base, accum)

    def _static_getmro(klass):
        '''Get a reasonable method resolution order of a class.

        Works well for both old-style and new-style classes.

        '''
        try:
            old_class_type = types.ClassType
        except AttributeError:
            # Python 3.1 lacks both getattr_static and ClassType
            class ClassType(type):
                '''Impossible class type.'''
            old_class_type = ClassType
        if isinstance(klass, type):
            return type.__dict__['__mro__'].__get__(klass)
        elif isinstance(klass, old_class_type):
            res = []
            _safe_search_bases(klass, res)
            return res
        else:
            msg = "doesn't apply to '%s' object"
            raise TypeError(msg % _typeof(klass).__name__)

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
        except StandardException:
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
                _desc = isinstance(class_dict, types.GetSetDescriptorType)
                if (not _desc and class_dict.__name__ == "__dict__" and
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
            _member = types.MemberDescriptorType
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
    `getattr_static`:func:.

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
        except BaseException:
            res = _undef
    if res is _undef and not is_type:
        cls = type(obj)
        res = getattr_static(cls, name, _undef)
        if isdatadescriptor(res):
            try:
                res = res.__get__(obj, cls)
            except StandardException:
                try:
                    res = res.__get__(cls, type)
                except StandardException:
                    res = _undef
    if res is not _undef:
        return res
    elif default is not _undef:
        return default
    else:
        from xoutil.eight import typeof
        msg = "'%s' object has no attribute '%s'"
        raise AttributeError(msg % (typeof(obj).__name__, name))


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
    named_types = class_types + (types.FunctionType, types.MethodType)
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


# TODO: Implement a safe version for `attrgetter`

if not getattr(_pm, 'getfullargspec', None):
    from xoutil.collections import namedtuple
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
