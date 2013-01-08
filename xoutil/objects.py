#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.objutil
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodríguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Feb 17, 2012

'''
Several utilities for objects in general.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)


from collections import Mapping
from functools import partial
from xoutil.types import Unset, is_collection
from xoutil.compat import str_base

__docstring_format__ = 'rst'
__author__ = 'manu'


# These two functions can be use to always return True or False
_true = lambda * args, **kwargs: True
_false = lambda * args, **kwargs: False



def smart_get(obj):
    return obj.get if isinstance(obj, Mapping) else partial(getattr, obj)


def xdir(obj, attr_filter=None, value_filter=None, getter=None):
    '''
    Return all ``(attr, value)`` pairs from `obj` that ``attr_filter(attr)``
    and ``value_filter(value)`` are both True.

    :param obj: The object to be instrospected.

    :param attr_filter: *optional* A filter for attribute names.

    :param value_filter: *optional* A filter for attribute values.

    :param getter: *optional* A function with the same signature that
                    ``getattr`` to be used to get the values from `obj`.

    If neither `attr_filter` nor `value_filter` are given, all `(attr, value)`
    are generated.

    '''
    getter = getter or getattr
    attrs = dir(obj)
    if attr_filter:
        attrs = (attr for attr in attrs if attr_filter(attr))
    res = ((a, getter(obj, a)) for a in attrs)
    if value_filter:
        res = ((a, v) for a, v in res if value_filter(v))
    return res


def fdir(obj, attr_filter=None, value_filter=None, getter=None):
    '''
    Similar to :func:`xdir` but yields only the attributes names.
    '''
    return (attr for attr, _v in xdir(obj, attr_filter, value_filter, getter))


def validate_attrs(source, target, force_equals=(), force_differents=()):
    '''
    Makes a 'comparison' of `source` and `target` by its attributes (or keys).

    This function returns True if and only if both of these tests
    pass:

    - All attributes in `force_equals` are equal in `source` and `target`

    - All attributes in `force_differents` are different in `source` and
      `target`

    For instance::

        >>> class Person(object):
        ...    def __init__(self, **kwargs):
        ...        for which in kwargs:
        ...            setattr(self, which, kwargs[which])

        >>> source = Person(**{b'name': 'Manuel', b'age': 33, b'sex': 'male'})
        >>> target = {b'name': 'Manuel', b'age': 4, b'sex': 'male'}

        >>> validate_attrs(source, target, force_equals=(b'sex',),
        ...                force_differents=(b'age',))
        True

        >>> validate_attrs(source, target, force_equals=(b'age',))
        False

    If both `force_equals` and `force_differents` are empty it will
    return True::

        >>> validate_attrs(source, target)
        True

    '''
    from operator import eq, ne
    res = True
    tests = ((ne, force_equals), (eq, force_differents))
    j = 0
    get_from_source = smart_get(source)
    get_from_target = smart_get(target)
    while res and  (j < len(tests)):
        fail, attrs = tests[j]
        i = 0
        while res and  (i < len(attrs)):
            attr = attrs[i]
            if fail(get_from_source(attr), get_from_target(attr)):
                res = False
            else:
                i += 1
        j += 1
    return res


def get_first_of(source, *keys, **kwargs):
    '''
    Return the first occurrence of any of the specified keys in `source`. If
    `source` is a tuple, a list, a set, or a generator; then the keys are
    searched in all the items.

    Examples:

    - To search some keys (whatever is found first) from a dict::

        >>> somedict = {"foo": "bar", "spam": "eggs"}
        >>> get_first_of(somedict, "no", "foo", "spam")
        'bar'

    - If a key/attr is not found, None is returned::

        >>> somedict = {"foo": "bar", "spam": "eggs"}
        >>> get_first_of(somedict, "eggs") is None
        True

    - Objects may be sources as well::

        >>> class Someobject(object): pass
        >>> inst = Someobject()
        >>> inst.foo = 'bar'
        >>> inst.eggs = 'spam'
        >>> get_first_of(inst, 'no', 'eggs', 'foo')
        'spam'

        >>> get_first_of(inst, 'invalid') is None
        True

    - You may pass several sources in a list, tuple or generator, and
      `get_first` will try each object at a time until it finds any of
      the key on a object; so any object that has one of the keys will
      "win"::

        >>> somedict = {"foo": "bar", "spam": "eggs"}
        >>> class Someobject(object): pass
        >>> inst = Someobject()
        >>> inst.foo = 'bar2'
        >>> inst.eggs = 'spam'
        >>> get_first_of((somedict, inst), 'eggs')
        'spam'

        >>> get_first_of((somedict, inst), 'foo')
        'bar'

        >>> get_first_of((inst, somedict), 'foo')
        'bar2'

        >>> get_first_of((inst, somedict), 'foobar') is None
        True

    You may pass a keywork argument called `default` with the value
    you want to be returned if no key is found in source::

        >>> none = object()
        >>> get_first_of((inst, somedict), 'foobar', default=none) is none
        True

    '''

    def inner(source):
        get = smart_get(source)
        res, i = Unset, 0
        while (res is Unset) and (i < len(keys)):
            res = get(keys[i], Unset)
            i += 1
        return res

    if is_collection(source):
        from itertools import imap, takewhile
        res = Unset
        for item in takewhile(lambda _: res is Unset, imap(inner, source)):
            if item is not Unset:
                res = item
    else:
        res = inner(source)
    return res if res is not Unset else kwargs.get('default', None)


def smart_getattr(name, *sources, **kwargs):
    '''Gets an attr by `name` for the first source that has it::

        >>> somedict = {'foo': 'bar', 'spam': 'eggs'}
        >>> class Some(object): pass
        >>> inst = Some()
        >>> inst.foo = 'bar2'
        >>> inst.eggs = 'spam'

        >>> smart_getattr('foo', somedict, inst)
        'bar'

        >>> smart_getattr('foo', inst, somedict)
        'bar2'

        >>> smart_getattr('fail', somedict, inst) is Unset
        True

    You may pass all keyword arguments supported by
    :func:`get_first_of`_.

    '''
    from xoutil.iterators import dict_update_new
    dict_update_new(kwargs, {'default': Unset})
    return get_first_of(sources, name, **kwargs)


def get_and_del_attr(obj, name, default=None):
    '''
    Looks for an attribute in the `obj` and returns its value and removes the
    attribute. If the attribute is not found, `default` is returned instead.

    '''
    res = getattr(obj, name, Unset)
    if res is Unset:
        res = default
    else:
        try:
            delattr(obj, name)
        except AttributeError:
            try:
                delattr(obj.__class__, name)
            except AttributeError:
                pass
    return res


def setdefaultattr(obj, name, value):
    '''Sets the attribute name to value if it is not set::

        >>> class Someclass(object): pass
        >>> inst = Someclass()
        >>> setdefaultattr(inst, 'foo', 'bar')
        'bar'

        >>> inst.foo
        'bar'

        >>> inst.spam = 'egg'
        >>> setdefaultattr(inst, 'spam', 'with ham')
        'egg'

    '''
    res = getattr(obj, name, Unset)
    if res is Unset:
        setattr(obj, name, value)
        res = value
    return res


def nameof(target):
    '''Gets the name of an object:

    - The name of a string is the same string::

        >>> nameof('manuel')
        'manuel'

    - The name of an object with a ``__name__`` attribute is its
      value::

        >>> nameof(type)
        'type'

        >>> class Someclass: pass
        >>> nameof(Someclass)
        'Someclass'

    - The name of any other object is the ``__name__`` of the its
      type::

        >>> nameof([1, 2])
        'list'

        >>> nameof((1, 2))
        'tuple'

        >>> nameof({})
        'dict'

    '''
    if isinstance(target, str_base):
        return target
    else:
        if not hasattr(target, '__name__'):
            target = type(target)
        return target.__name__


def full_nameof(target):
    '''Gets the full name of an object:

    - The name of a string is the same string::

        >>> full_nameof('manuel')
        'manuel'

    - The name of an object with a ``__name__`` attribute is its
      value::

        >>> full_nameof(type)
        'type'

        >>> class Someclass: pass
        >>> full_nameof(Someclass) == 'xoutil.objects.Someclass'
        True

    - The name of any other object is the ``__name__`` of the its
      type::

        >>> full_nameof([1, 2])
        'list'

        >>> full_nameof((1, 2))
        'tuple'

        >>> full_nameof({})
        'dict'

    '''
    if isinstance(target, str_base):
        return target
    else:
        if not hasattr(target, '__name__'):
            target = type(target)
        res = target.__name__
        mod = getattr(target, '__module__', '__')
        if not mod.startswith('__'):
            res = '.'.join((mod, res))
        return res



__all__ = [str(item)
             for item in ('xdir', 'fdir', 'validate_attrs', 'get_first_of',
                          'smart_getattr', 'get_and_del_attr',
                          'setdefaultattr', 'nameof', 'full_nameof')]
