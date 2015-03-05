#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.objects
# ---------------------------------------------------------------------
# Copyright (c) 2012-2015 Merchise Autrement
# All rights reserved.
#
# Author: Medardo Rodríguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created 2012-02-17

'''Several utilities for objects in general.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

from xoutil import Unset
from six import PY3 as _py3k, callable, string_types as str_base
from xoutil.deprecation import deprecated


__docstring_format__ = 'rst'


_INVALID_CLASS_TYPE_MSG = '``cls`` must be a class not an instance'

# Safe length
_len = lambda x: len(x) if x else 0

# These two functions can be use to always return True or False
_true = lambda *args, **kwargs: True
_false = lambda *args, **kwargs: False


class SafeDataItem(object):
    '''A data descriptor that is safe.

    A *safe descriptor* never uses internal special methods ``__getattr__``
    and ``__getattribute__`` to obtain its value.  Also allow to define a
    constructor or a default value for the first time the attribute is read
    without a prior value assigned.

    This class only can be instanced inner a class context in one of the
    following scenarios::

    1. As a normal descriptor not associated with a constructor method::

        >>> from xoutil.objects import SafeDataItem as safe
        >>> class Foobar(object):
        ...     safe('mapping', dict)
        >>> f = Foobar()
        >>> f.mapping
        {}

    2. As a normal descriptor but associated with a constructor method::

        >>> class Foobar(object):
        ...     @safe.property
        ...     def mapping(self):
        ...         return {'this': self}
        >>> f = Foobar()
        >>> f.mapping['this'] is f
        True

    3. As a slot.  In this case generate an internal slot and a safe
       descriptor to access it::

        >>> class Foobar(object):
        ...     __slots__ = safe.slot('mapping', dict)
        >>> f = Foobar()
        >>> f.mapping
        {}

    '''

    def __init__(self, *args, **kwargs):
        '''Creates a new safe descriptor.

        Arguments are parsed to discover:

        - An attribute name if a string with a valid identifier is given as a
          positional argument.

        - A constructor for initial or default value when the descriptor is
          read without being assigned.  Positional argument with a callable.

        - Default literal value is given using a keyword argument with any of
          the following names: `default`, `value` or `initial_value`.  If this
          argument is given the constructor callable is invalid.

        - A function to check value validity with the keyword argument with
          any of the following names: `validator`, `checker` or `check`.

        - Boolean `False` to avoid assigning the descriptor in the class
          context with the keyword argument `do_assigning`.  Any other value
          but `False` is invalid because this concept is implicitly required
          and use a `False` value is allowed but discouraged.

        '''
        self.__parse_arguments(*args, **kwargs)
        if self.do_assigning:
            cls_locals = self._get_class_context()
            current = cls_locals.get(self.attr_name)
            if not isinstance(current, SafeDataItem):
                cls_locals[self.attr_name] = self
            else:
                msg = ('class `%s` has already an assigned descriptor with '
                       'the same name `%s`')
                type_name = type(self).__name__
                raise AttributeError(msg % (type_name, self.attr_name))

    @staticmethod
    def slot(slot_name, *args, **kwargs):
        '''Generate an internal slot and this descriptor to access it.

        This must appears in a slots declaration::

          class Foobar(object):
              __slots__ = (SafeDataItem.slot('mapping', dict), ...)

        This method return the inner slot name, argument passed is used for
        the safe descriptor.  In the example above the slot descriptor will be
        `__mapping__` and `mapping` the safe descriptor.

        '''
        self = SafeDataItem(slot_name, *args, **kwargs)
        return self.inner_name

    @staticmethod
    def property(*args, **kwargs):
        '''Descriptor to access a property value based in a method.

        There are two ways of use this method:

        - With only one positional and no keyword arguments.  The positional
          argument must be a method which is assumed as the constructor of the
          original property value.  Method name is used as the attribute name.
          In this case it returns a safe descriptor::

            >>> from xoutil.objects import SafeDataItem as safe
            >>> class Foobar(object):
            ...     @safe.property
            ...     def mapping(self):
            ...         'To generate a safe `mapping` descriptor.'
            ...         return {'this': self}
            >>> f = Foobar()
            >>> f.mapping['this'] is f
            True

        - With no positional and with keyword arguments.  In this case it
          returns a decorator that receive one single argument (the method)
          and return the safe descriptor::

            >>> class Foobar(object):
            ...     @safe.property(kind='class')
            ...     def mapping(cls):
            ...         'To generate a safe `mapping` descriptor.'
            ...         return {'this': cls}
            >>> f = Foobar()
            >>> f.mapping['this'] is Foobar
            True


        Returns the safe descriptor instance if only the method is given, or a
        closure if additional keyword arguments are given.

        Additional keyword argument `kind` could be 'normal' (for normal
        methods), 'static' (for static methods), and 'class' (for class
        methods)::

        '''
        def inner(method):
            from types import FunctionType as function
            from xoutil.validators import check
            FUNC_KINDS = ('normal', 'static', 'class')
            FUNC_TYPES = (function, staticmethod, classmethod)
            KIND_NAME = 'kind'
            kind = kwargs.pop(KIND_NAME, FUNC_KINDS[0])
            if (check(kind, lambda k: k in FUNC_KINDS)
                    and check(method, FUNC_TYPES)):
                kwargs['do_assigning'] = False

                def init():
                    from sys import _getframe
                    obj = _getframe(1).f_locals['obj']
                    if kind == FUNC_KINDS[0]:
                        return method(obj)
                    elif kind == FUNC_KINDS[1]:
                        return method()
                    else:
                        return method(type(obj))

                init.__name__ = method.__name__
                return SafeDataItem(init, **kwargs)

        if kwargs:
            return inner
        elif len(args) == 1:
            return inner(args[0])
        else:
            msg = 'expected only one positional argument, got %s'
            raise TypeError(msg % len(args))

    def __get__(self, obj, owner):
        if obj is not None:
            from xoutil.inspect import get_attr_value
            res = get_attr_value(obj, self.inner_name, Unset)
            if res is not Unset:
                return res
            elif self.init is not Unset:
                try:
                    res = self.init()
                except:
                    print('>>>', self.init, '::', type(self.init))
                    raise
                self.__set__(obj, res)
                return res
            elif self.default is not Unset:
                res = self.default
                self.__set__(obj, res)
                return res
            else:
                msg = "'%s' object has no attribute '%s'"
                raise AttributeError(msg % (type(obj).__name__,
                                            self.attr_name))
        else:
            return self

    def __set__(self, obj, value):
        object.__setattr__(obj, self.inner_name, value)

    def __delete__(self, obj):
        object.__delattr__(obj, self.inner_name)

    def _get_class_context(self):
        'Get the class variable context'
        from sys import _getframe
        frame = _getframe(1)
        i, MAX = 0, 5
        res = None
        while not res and (i < MAX):
            aux = frame.f_locals
            if '__module__' in aux:
                res = aux
            else:
                frame = frame.f_back
                i += 1
        if res:
            return res
        else:
            msg = ('Invalid `SafeDataItem(%s)` call, must be used in a class '
                   'context.')
            raise TypeError(msg % self.attr_name)

    def _unique_name(self):
        '''Generate a unique new name.'''
        from time import time
        from xoutil.bases import int2str
        return '_%s' % int2str(int(1000000*time()))

    def __parse_arguments(self, *args, **kwargs):
        '''Assign parsed arguments to the just created instance.'''
        from xoutil.validators import (is_type, is_valid_identifier)
        self.attr_name = Unset
        self.init = Unset
        self.default = Unset
        self.do_assigning = True
        self.validator = _true
        for i, arg in enumerate(args):
            if self.attr_name is Unset and is_valid_identifier(arg):
                self.attr_name = arg
            elif self.init is Unset and callable(arg):
                self.init = arg
            else:
                msg = ('Invalid positional arguments: %s at %s\n'
                       'Valid arguments are the attribute name and a '
                       'callable constructor for initial value.')
                raise ValueError(msg % (args[i:], i))
        bads = {}
        for key in kwargs:
            value = kwargs[key]
            if (self.default is Unset and self.init is Unset and
                    key in ('default', 'value', 'initial_value')):
                self.default = value
            elif (self.validator is _true and callable(value) and
                  key in ('validator', 'checker', 'check')):
                if isinstance(value, type):
                    self.validator = is_type(value)
                else:
                    self.validator = value
            elif (self.do_assigning is True and key == 'do_assigning' and
                  value is False):
                self.do_assigning = False
            else:
                bads[key] = value
        if bads:
            msg = ('Invalid keyword arguments: %s\n'
                   'See constructor documentation for more info.')
            raise ValueError(msg % bads)
        if self.attr_name is Unset:
            from xoutil.names import nameof
            if self.init is not Unset:
                if isinstance(self.init, type):
                    self.attr_name = str('_%s' % self.init.__name__)
                else:
                    self.attr_name = nameof(self.init, safe=True)
            else:
                self.attr_name = self._unique_name()
        self.inner_name = str('__%s__' % self.attr_name.strip('_'))


def smart_getter(obj, strict=False):
    '''Returns a smart getter for `obj`.

    If obj is Mapping, it returns the ``.get()`` method bound to the object
    `obj`.  Otherwise it returns a partial of `getattr` on `obj` with default
    set to None (if `strict` is False).

    :param strict: Set this to True so that the returned getter checks that
                   keys/attrs exists.  If `strict` is True the getter may
                   raise a KeyError or an AttributeError.

    .. versionchanged:: 1.5.3 Added the parameter `strict`.

    '''
    from collections import Mapping
    from xoutil.types import DictProxyType
    if isinstance(obj, (DictProxyType, Mapping)):
        if not strict:
            return obj.get
        else:
            def _get(key, default=Unset):
                try:
                    return obj[key]
                except KeyError:
                    if default is Unset:
                        raise
                    else:
                        return default
            return _get
    else:
        if not strict:
            return lambda attr, default=None: getattr(obj, attr, default)
        else:
            def _partial(attr, default=Unset):
                try:
                    return getattr(obj, attr)
                except AttributeError:
                    if default is Unset:
                        raise
                    else:
                        return default
            return _partial


def smart_getter_and_deleter(obj):
    '''Returns a function that get and deletes either a key or an attribute of
    obj depending on the type of `obj`.

    If `obj` is a `collections.Mapping` it must be a
    `collections.MutableMapping`.

    '''
    from collections import Mapping, MutableMapping
    from functools import partial
    if isinstance(obj, Mapping) and not isinstance(obj, MutableMapping):
        raise TypeError('If `obj` is a Mapping it must be a MutableMapping')
    if isinstance(obj, MutableMapping):
        return lambda key, default=None: obj.pop(key, default)
    else:
        return partial(popattr, obj)


def is_private_name(name):
    '''Return if `name` is private or not.'''
    prefix = '__'
    return name.startswith(prefix) and not name.endswith(prefix)


def fix_private_name(cls, name):
    '''Correct a private name with Python conventions, return the same value if
    name is not private.

    '''
    if is_private_name(name):
        return str('_%s%s' % (cls.__name__, name))
    else:
        return name


# TODO: [med] [manu] Decide if it's best to create a 'xoutil.inspect' that
# extends the standard library module 'inspect' and place this
# signature-dealing functions there. Probably, to be consistent, this imposes a
# refactoring of some of 'xoutil.types' and move all the "is_classmethod",
# "is_staticmethod" and inspection-related functions there.
def get_method_function(cls, method_name):
    '''Get definition function given in its :param:`method_name`.

    There is a difference between the result of this function and
    ``getattr(cls, method_name)`` because the last one return the unbound
    method and this a python function.

    '''
    if not isinstance(cls, type):
        cls = cls.__class__
    mro = cls.mro()
    i, res = 0, None
    while not res and (i < len(mro)):
        sc = mro[i]
        method = sc.__dict__.get(method_name)
        if callable(method):
            res = method
        else:
            i += 1
    return res


def build_documentation(cls, get_doc=None, deep=1):
    '''Build a proper documentation from a class :param:`cls`.

    Classes are recursed in MRO until process all levels (:param:`deep`)
    building the resulting documentation.

    The function :param:`get_doc` get the documentation of a given class. If
    no function is given, then attribute ``__doc__`` is used.

    '''
    from xoutil.string import safe_decode
    assert isinstance(cls, type), _INVALID_CLASS_TYPE_MSG
    if deep < 1:
        deep = 1
    get_doc = get_doc or (lambda c: c.__doc__)
    mro = cls.mro()
    i, level, used, res = 0, 0, {}, ''
    while (level < deep) and (i < len(mro)):
        sc = mro[i]
        doc = get_doc(sc)
        if doc:
            doc = safe_decode(doc).strip()
            key = sc.__name__
            docs = used.setdefault(key, set())
            if doc not in docs:
                docs.add(doc)
                if res:
                    res += '\n\n'
                res += '=== <%s> ===\n\n%s' % (key, doc)
                level += 1
        i += 1
    return res


def fix_class_documentation(cls, ignore=None, min_length=10, deep=1,
                            default=None):
    '''Fix the documentation for the given class using its super-classes.

    This function may be useful for shells or Python Command Line Interfaces
    (CLI).

    If :param:`cls` has an invalid documentation, super-classes are recursed
    in MRO until a documentation definition was made at any level.

    :param:`ignore` could be used to specify which classes to ignore by
                    specifying its name in this list.

    :param:`min_length` specify that documentations with less that a number of
                        characters, also are ignored.

    '''
    assert isinstance(cls, type), _INVALID_CLASS_TYPE_MSG
    if _len(cls.__doc__) < min_length:
        ignore = ignore or ()

        def get_doc(c):
            if (c.__name__ not in ignore) and _len(c.__doc__) >= min_length:
                return c.__doc__
            else:
                return None

        doc = build_documentation(cls, get_doc, deep)
        if doc:
            cls.__doc__ = doc
        elif default:
            cls.__doc__ = default(cls) if callable(default) else default


def fix_method_documentation(cls, method_name, ignore=None, min_length=10,
                             deep=1, default=None):
    '''Fix the documentation for the given class using its super-classes.

    This function may be useful for shells or Python Command Line Interfaces
    (CLI).

    If :param:`cls` has an invalid documentation, super-classes are recursed
    in MRO until a documentation definition was made at any level.

    :param:`ignore` could be used to specify which classes to ignore by
                    specifying its name in this list.

    :param:`min_length` specify that documentations with less that a number of
                        characters, also are ignored.

    '''
    assert isinstance(cls, type), _INVALID_CLASS_TYPE_MSG
    method = get_method_function(cls, method_name)
    if method and _len(method.__doc__) < min_length:
        ignore = ignore or ()

        def get_doc(c):
            if (c.__name__ not in ignore):
                method = c.__dict__.get(method_name)
                if callable(method) and _len(method.__doc__) >= min_length:
                    return method.__doc__
                else:
                    return None
            else:
                return None

        doc = build_documentation(cls, get_doc, deep)
        if doc:
            method.__doc__ = doc
        elif default:
            method.__doc__ = default(cls) if callable(default) else default


def fulldir(obj):
    '''Return a set with all attribute names defined in `obj`'''
    res = set()
    if isinstance(obj, type):
        for cls in type.mro(obj):
            res |= set(SafeDataItem.getattr(cls, '__dict__', {}))
    else:
        res |= set(SafeDataItem.getattr(obj, '__dict__', {}))
    cls = type(obj)
    if cls is not type:
        res |= set(dir(cls))
    return res


# TODO: Fix signature after removal of attr_filter and value_filter
def xdir(obj, attr_filter=None, value_filter=None, getter=None, filter=None, _depth=0):
    '''Return all ``(attr, value)`` pairs from `obj` that ``attr_filter(attr)``
    and ``value_filter(value)`` are both True.

    :param obj: The object to be instrospected.

    :param filter: *optional* A filter that will be passed both the attribute
       name and it's value as two positional arguments. It should return True
       for attrs that should be yielded.

       .. note::

          If passed, both `attr_filter` and `value_filter` will be
          ignored.

    :param attr_filter: *optional* A filter for attribute names. *Deprecated
         since 1.4.1*

    :param value_filter: *optional* A filter for attribute values. *Deprecated
         since 1.4.1*

    :param getter: *optional* A function with the same signature that
                   ``getattr`` to be used to get the values from `obj`.

    .. deprecated:: 1.4.1 The use of params `attr_filter` and `value_filter`.

    '''
    getter = getter or getattr
    attrs = dir(obj)
    if attr_filter or value_filter:
        import warnings
        msg = ('Arguments of `attr_filter` and `value_filter` are deprecated. '
               'Use argument `filter` instead.')
        warnings.warn(msg, stacklevel=_depth + 1)
    if filter:
        attr_filter = None
        value_filter = None
    if attr_filter:
        attrs = (attr for attr in attrs if attr_filter(attr))
    res = ((a, getter(obj, a)) for a in attrs)
    if value_filter:
        res = ((a, v) for a, v in res if value_filter(v))
    if filter:
        res = ((a, v) for a, v in res if filter(a, v))
    return res


# TODO: Fix signature after removal of attr_filter and value_filter
def fdir(obj, attr_filter=None, value_filter=None, getter=None, filter=None):
    '''Similar to :func:`xdir` but yields only the attributes names.'''
    full = xdir(obj,
                filter=filter,
                attr_filter=attr_filter,
                value_filter=value_filter,
                getter=getter,
                _depth=1)
    return (attr for attr, _v in full)


def validate_attrs(source, target, force_equals=(), force_differents=()):
    '''Makes a 'comparison' of `source` and `target` by its attributes (or
    keys).

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

        >>> source = Person(name='Manuel', age=33, sex='male')
        >>> target = {'name': 'Manuel', 'age': 4, 'sex': 'male'}

        >>> validate_attrs(source, target, force_equals=('sex',),
        ...                force_differents=('age',))
        True

        >>> validate_attrs(source, target, force_equals=('age',))
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
    get_from_source = smart_getter(source)
    get_from_target = smart_getter(target)
    while res and (j < len(tests)):
        fail, attrs = tests[j]
        i = 0
        while res and (i < len(attrs)):
            attr = attrs[i]
            if fail(get_from_source(attr), get_from_target(attr)):
                res = False
            else:
                i += 1
        j += 1
    return res


def iterate_over(source, *keys):
    '''Yields pairs of (key, value) for of all `keys` in `source`.

    If any `key` is missing from `source` is ignored (not yielded).

    If `source` is a `collection <xoutil.types.is_collection>`:func:, iterate
    over each of the items searching for any of keys.  This is not recursive.

    If no `keys` are provided, return an "empty" iterator -- i.e will raise
    StopIteration upon calling `next`.

    .. versionadded:: 1.5.2

    '''
    from xoutil.types import is_collection

    def inner(source):
        get = smart_getter(source)
        for key in keys:
            val = get(key, Unset)
            if val is not Unset:
                yield key, val

    def when_collection(source):
        from six.moves import map
        for generator in map(inner, source):
            for key, val in generator:
                yield key, val

    if is_collection(source):
        res = when_collection(source)
    else:
        res = inner(source)
    return res


def get_first_of(source, *keys, **kwargs):
    '''Return the value of the first occurrence of any of the specified `keys`
    in `source` that matches `pred` (if given).

    Both `source` and `keys` has the same meaning as in :func:`iterate_over`.

    :param default: A value to be returned if no key is found in `source`.

    :param pred:  A function that should receive a single value and return
                  False if the value is not acceptable, and thus
                  `get_first_of` should look for another.

    .. versionchanged:: 1.5.2  Added the `pred` option.

    '''
    default = kwargs.pop('default', None)
    pred = kwargs.pop('pred', None)
    if kwargs:
        raise TypeError('Invalid keywords %s for get_first_of' %
                        (kwargs.keys(), ))
    _key, res = next(((k, val) for k, val in iterate_over(source, *keys)
                      if not pred or pred(val)), (Unset, Unset))
    return res if res is not Unset else default


def pop_first_of(source, *keys, **kwargs):
    '''Similar to :func:`get_first_of` using as `source` either an object or a
    mapping and deleting the first attribute or key.

    Examples::

        >>> somedict = dict(bar='bar-dict', eggs='eggs-dict')

        >>> class Foo(object): pass
        >>> foo = Foo()
        >>> foo.bar = 'bar-obj'
        >>> foo.eggs = 'eggs-obj'

        >>> pop_first_of((somedict, foo), 'eggs')
        'eggs-dict'

        >>> pop_first_of((somedict, foo), 'eggs')
        'eggs-obj'

        >>> pop_first_of((somedict, foo), 'eggs') is None
        True

        >>> pop_first_of((foo, somedict), 'bar')
        'bar-obj'

        >>> pop_first_of((foo, somedict), 'bar')
        'bar-dict'

        >>> pop_first_of((foo, somedict), 'bar') is None
        True

    '''
    from xoutil.types import is_collection

    def inner(source):
        get = smart_getter_and_deleter(source)
        res, i = Unset, 0
        while (res is Unset) and (i < len(keys)):
            res = get(keys[i], Unset)
            i += 1
        return res

    if is_collection(source):
        res = Unset
        source = iter(source)
        probe = next(source, None)
        while res is Unset and probe:
            res = inner(probe)
            probe = next(source, None)
    else:
        res = inner(source)
    return res if res is not Unset else kwargs.get('default', None)


get_and_del_first_of = deprecated(pop_first_of)(pop_first_of)


@deprecated(get_first_of)
def smart_getattr(name, *sources, **kwargs):
    '''Gets an attr by `name` for the first source that has it.

    This is roughly that same as::

       get_first_of(sources, name, default=Unset, **kwargs)

    .. warning:: Deprecated since 1.5.1

    '''
    from xoutil.iterators import dict_update_new
    dict_update_new(kwargs, {'default': Unset})
    return get_first_of(sources, name, **kwargs)


def popattr(obj, name, default=None):
    '''Looks for an attribute in the `obj` and returns its value and removes
    the attribute. If the attribute is not found, `default` is returned
    instead.

    Examples::

        >>> class Foo(object):
        ...   a = 1
        >>> foo = Foo()
        >>> foo.a = 2
        >>> popattr(foo, 'a')
        2
        >>> popattr(foo, 'a')
        1
        >>> popattr(foo, 'a') is None
        True

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

get_and_del_attr = deprecated(popattr)(popattr)


class lazy(object):
    '''Marks a value as a lazily evaluated value. See
    :func:`setdefaultattr`.

    '''
    def __init__(self, value, *args, **kwargs):
        self.value = value
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        from six import callable
        res = self.value
        if callable(res):
            return res(*self.args, **self.kwargs)
        else:
            return res


def mixin(base):
    '''Create a valid mixin base.

    If several mixins with the same base are used all-together in a class
    inheritance, Python generates ``TypeError: multiple bases have instance
    lay-out conflict``.  To avoid that, inherit from the class this function
    returns instead of desired :param:`base`.

    '''
    org = "\n\nOriginal doc:\n\n%s" % base.__doc__ if base.__doc__ else ''
    doc = "Generated mixin base from %s.%s" % (repr(base), org)
    name = str('%s_base_mixin' % base.__name__)
    return type(name, (base,), {'__doc__': doc})


class classproperty(object):
    '''A descriptor that behaves like property for instances but for classes.

    Example of its use::

        class Foobar(object):
            @classproperty
            def getx(cls):
                return cls._x

    Class properties are always read-only, if attribute values must be set or
    deleted, a metaclass must be defined.

    '''
    def __init__(self, fget):
        '''Create the class property descriptor.

          :param fget: is a function for getting the class attribute value

        '''
        self.__get = fget

    def __get__(self, instance, owner):
        cls = type(instance) if instance is not None else owner
        return self.__get(cls)


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

    (`New in version 1.2.1`). If you want the value to be lazily evaluated you
    may provide a lazy-lambda::

        >>> inst = Someclass()
        >>> inst.a = 1
        >>> def setting_a():
        ...    print('Evaluating!')
        ...    return 'a'

        >>> setdefaultattr(inst, 'a', lazy(setting_a))
        1

        >>> setdefaultattr(inst, 'ab', lazy(setting_a))
        Evaluating!
        'a'

    '''
    res = getattr(obj, name, Unset)
    if res is Unset:
        if isinstance(value, lazy):
            value = value()
        setattr(obj, name, value)
        res = value
    return res


def copy_class(cls, meta=None, ignores=None, new_attrs=None):
    '''Copies a class definition to a new class.

    The returned class will have the same name, bases and module of `cls`.

    :param meta: If None, the `type(cls)` of the class is used to build the new
                 class, otherwise this must be a *proper* metaclass.


    :param ignores: A (sequence of) string, glob-pattern, or regexp for
                    attributes names that should not be copied to new class.

                    If the strings begins with "(?" it will be considered a
                    regular expression string representation, if it does not
                    but it contains any wild-char it will be considered a
                    glob-pattern, otherwise is the exact name of the ignored
                    attribute.

                    Any ignored that is not a string **must** be an object with
                    a `match(attr)` method that must return a non-null value if
                    the the `attr` should be ignored. For instance, a regular
                    expression object.

    :param new_attrs: New attributes the class must have. These will take
                      precedence over the attributes in the original class.

    :type new_attrs: dict

    .. versionadded:: 1.4.0

    '''
    from xoutil.fs import _get_regex
    from six import iteritems as iteritems_
    # TODO: [manu] "xoutil.fs" is more specific module than this one. So ...
    #       isn't correct to depend on it. Migrate part of "_get_regex" to a
    #       module that can be imported logically without problems from both,
    #       this and "xoutil.fs".
    from xoutil.types import MemberDescriptorType
    if not meta:
        meta = type(cls)
    if isinstance(ignores, str_base):
        ignores = (ignores, )
        ignores = tuple((_get_regex(i) if isinstance(i, str_base) else i) for i in ignores)
        ignored = lambda name: any(ignore.match(name) for ignore in ignores)
    else:
        ignored = None
    valids = ('__class__', '__mro__', '__name__', '__weakref__', '__dict__')
    attrs = {name: value
             for name, value in iteritems_(cls.__dict__)
             if name not in valids
             # Must remove member descriptors, otherwise the old's class
             # descriptor will override those that must be created here.
             if not isinstance(value, MemberDescriptorType)
             if ignored is None or not ignored(name)}
    if new_attrs:
        attrs.update(new_attrs)
    result = meta(cls.__name__, cls.__bases__, attrs)
    return result


# Real signature is (*sources, target, *, default=None) where target is a
# positional argument, and not a keyword.
# TODO: First look up "target" in keywords and then in positional arguments.
def smart_copy(*args, **kwargs):
    '''Copies the first apparition of attributes (or keys) from `sources` to
    `target`.

    :param sources: The objects from which to extract keys or attributes.

    :param target: The object to fill.

    :param defaults: Default values for the attributes to be copied as
                     explained below. Defaults to False.

    :type defaults: Either a bool, a dictionary, an iterable or a callable.

    Every `sources` and `target` are always positional arguments. There should
    be at least one source. `target` will always be the last positional
    argument.

    If `defaults` is a dictionary or an iterable then only the names provided
    by itering over `defaults` will be copied. If `defaults` is a dictionary,
    and one of its key is not found in any of the `sources`, then the value of
    the key in the dictionary is copied to `target` unless:

    - It's the value :class:`xoutil.types.Required` or an instance of Required.

    - An exception object

    - A sequence with is first value being a subclass of Exception. In which
      case :class:`xoutil.data.adapt_exception` is used.

    In these cases a KeyError is raised if the key is not found in the sources.

    If `default` is an iterable and a key is not found in any of the sources,
    None is copied to `target`.

    If `defaults` is a callable then it should receive one positional arguments
    for the current `attribute name` and several keyword arguments (we pass
    ``source``) and return either True or False if the attribute should be
    copied.

    If `defaults` is False (or None) only the attributes that do not start with
    a "_" are copied, if it's True all attributes are copied.

    When `target` is not a mapping only valid Python identifiers will be
    copied.

    Each `source` is considered a mapping if it's an instance of
    `collections.Mapping` or a DictProxyType.

    The `target` is considered a mapping if it's an instance of
    `collections.MutableMapping`.

    :returns: `target`.

    .. versionchanged:: 1.6.9 `defaults` is now keyword only.

    '''
    from collections import Mapping, MutableMapping
    from xoutil.types import is_collection, Required
    from xoutil.types import DictProxyType
    from xoutil.data import adapt_exception
    from xoutil.validators.identifiers import is_valid_identifier
    defaults = kwargs.pop('defaults', False)
    if kwargs:
        raise TypeError('smart_copy does not accept a "%s" keyword argument'
                        % kwargs.keys()[0])
    sources, target = args[:-1], args[-1]
    if not sources:
        raise TypeError('smart_copy requires at least one source')
    if isinstance(target, (bool, type(None), int, float, str_base)):
        raise TypeError('target should be a mutable object, not %s' %
                        type(target))
    if isinstance(target, MutableMapping):
        def setter(key, val):
            target[key] = val
    else:
        def setter(key, val):
            if is_valid_identifier(key):
                setattr(target, key, val)
    is_mapping = isinstance(defaults, Mapping)
    if is_mapping or is_collection(defaults):
        for key, val in ((key, get_first_of(sources, key, default=Unset))
                         for key in defaults):
            if val is Unset:
                if is_mapping:
                    val = defaults.get(key, None)
                else:
                    val = None
                exc = adapt_exception(val, key=key)
                if exc or val is Required or isinstance(val, Required):
                    raise KeyError(key)
            setter(key, val)
    else:
        keys = []
        for source in sources:
            get = smart_getter(source)
            if isinstance(source, (Mapping, DictProxyType)):
                items = (name for name in source)
            else:
                items = dir(source)
            for key in items:
                private = isinstance(key, str_base) and key.startswith('_')
                if (defaults is False or defaults is None) and private:
                    copy = False
                elif callable(defaults):
                    copy = defaults(key, source=source)
                else:
                    copy = True
                if key not in keys:
                    keys.append(key)
                    if copy:
                        setter(key, get(key))
    return target


def extract_attrs(obj, *names, **kwargs):
    '''Extracts all `names` from an object.

    If `obj` is a Mapping, the names will be search in the keys of the `obj`;
    otherwise the names are considered regular attribute names.

    If `default` is Unset and any name is not found, an AttributeError is
    raised, otherwise the `default` is used instead.

    Returns a tuple if there are more that one name, otherwise returns a
    single value.

    .. versionadded:: 1.4.0

    .. versionchanged:: 1.5.3 Each `name` may be a path like in
       `get_traverser`:func:, but only "." is allowed as separator.

    '''
    default = kwargs.pop('default', Unset)
    if kwargs:
        raise TypeError('Invalid keyword arguments for `extract_attrs`')
    getter = get_traverser(*names, default=default)
    return getter(obj)


if _py3k:
    from xoutil import _meta3
    __m = _meta3
else:
    from xoutil import _meta2
    __m = _meta2

metaclass = __m.metaclass


metaclass.__doc__ = '''Define the metaclass of a class.

    .. versionadded:: 1.4.1

    This function allows to define the metaclass of a class equally in Python
    2 and 3.

    Usage::

       >>> class Meta(type):
       ...   pass

       >>> class Foobar(metaclass(Meta)):
       ...   pass

       >>> class Spam(metaclass(Meta), dict):
       ...   pass

       >>> type(Spam) is Meta
       True

       >>> Spam.__bases__ == (dict, )
       True

    .. versionadded:: 1.5.5 The `kwargs` keywords arguments with support for
       ``__prepare__``.

    Metaclasses are allowed to have a ``__prepare__`` classmethod to return
    the namespace into which the body of the class should be evaluated.  See
    :pep:`3115`.

    .. warning:: The :pep:`3115` is not possible to implement in Python 2.7.

       Despite our best efforts to have a truly compatible way of creating
       meta classes in both Python 2.7 and 3.0+, there is an inescapable
       difference in Python 2.7.  The :pep:`3115` states that ``__prepare__``
       should be called before evaluating the body of the class.  This is not
       possible in Python 2.7, since ``__new__`` already receives the
       attributes collected in the body of the class.  So it's always too late
       to call ``__prepare__`` at this point and the Python 2.7 interpreter
       does not call it.

       Our approach for Python 2.7 is calling it inside the ``__new__`` of a
       "side" metaclass that is used for the base class returned.  This means
       that ``__prepare__`` is called **only** for classes that use the
       `metaclass`:func: directly.  In the following hierarchy::

           class Meta(type):
                @classmethod
                def __prepare__(cls, name, bases, **kwargs):
                    from xoutil.collections import OrderedDict
                    return OrderedDict()

           class Foo(metaclass(Meta)):
                pass

           class Bar(Foo):
                pass

       when creating the class ``Bar`` the ``__prepare__()`` class method is
       not called in Python 2.7!

    .. seealso:: `xoutil.types.prepare_class`:func: and
       `xoutil.types.new_class`:func:.

    .. warning::

       You should always place your metaclass declaration *first* in the list
       of bases. Doing otherwise triggers *twice* the metaclass' constructors
       in Python 3.1 or less.

       If your metaclass has some non-idempotent side-effect (such as
       registration of classes), then this would lead to unwanted double
       registration of the class::

          >>> class BaseMeta(type):
          ...     classes = []
          ...     def __new__(cls, name, bases, attrs):
          ...         res = super(BaseMeta, cls).__new__(cls, name, bases, attrs)
          ...         cls.classes.append(res)   # <-- side effect
          ...         return res

          >>> class Base(metaclass(BaseMeta)):
          ...     pass

          >>> class SubType(BaseMeta):
          ...     pass

          >>> class Egg(metaclass(SubType), Base):   # <-- metaclass first
          ...     pass

          >>> Egg.__base__ is Base   # <-- but the base is Base
          True

          >>> len(BaseMeta.classes) == 2
          True

          >>> class Spam(Base, metaclass(SubType)):
          ...     'Like "Egg" but it will be registered twice in Python 2.x.'

       In this case the registration of Spam ocurred twice::

          >>> BaseMeta.classes  # doctest: +SKIP
          [<class Base>, <class Egg>, <class Spam>, <class Spam>]

       Bases, however, are just fine::

          >>> Spam.__bases__ == (Base, )
          True

'''


def register_with(abc):
    '''Register a virtual `subclass` of an ABC.

    For example::

        >>> from collections import Mapping
        >>> @register_with(Mapping)
        ... class Foobar(object):
        ...     pass

        >>> issubclass(Foobar, Mapping)
        True

    '''
    def inner(subclass):
        abc.register(subclass)
        return subclass
    return inner


def traverse(obj, path, default=Unset, sep='.', getter=None):
    '''Traverses an object's hierarchy by performing an attribute get at each
    level.

    This helps getting an attribute that is buried down several levels
    deep. For example::

       traverse(request, 'session.somevalue')

    If `default` is not provided (i.e is `~xoutil.Unset`:obj:) and any
    component in the path is not found an AttributeError exceptions is raised.

    You may provide `sep` to change the default separator.

    You may provide a custom `getter`.  By default, does an
    :func:`smart_getter` over the objects. If provided `getter` should have
    the signature of `getattr`:func:.

    See `get_traverser`:func: if you need to apply the same path(s) to several
    objects.  Actually this is equivalent to::

        get_traverser(path, default=default, sep=sep, getter=getter)(obj)

    '''
    _traverser = get_traverser(path, default=default, sep=sep, getter=None)
    return _traverser(obj)


def get_traverser(*paths, **kw):
    '''Combines the power of `traverse`:func: with the expectations from both
    `operator.itergetter`:func: and `operator.attrgetter`:func:.

    :param paths: Several paths to extract.

    Keyword arguments has the same meaning as in `traverse`:func:.

    :returns: A function the when invoked with an `object` traverse the object
              finding each `path`.

    .. versionadded:: 1.5.3

    '''
    def _traverser(path, default=Unset, sep='.', getter=None):
        if not getter:
            getter = lambda o, a, default=None: smart_getter(o)(a, default)

        def inner(obj):
            found = object()
            current = obj
            attrs = path.split(sep)
            while current is not found and attrs:
                attr = attrs.pop(0)
                current = getter(current, attr, found)
            if current is found:
                if default is Unset:
                    raise AttributeError(attr)
                else:
                    return default
            else:
                return current

        return inner

    if len(paths) == 1:
        result = _traverser(paths[0], **kw)
    elif len(paths) > 1:
        _traversers = tuple(_traverser(path, **kw) for path in paths)

        def _result(obj):
            return tuple(traverse(obj) for traverse in _traversers)

        result = _result
    else:
        raise TypeError('"get_traverser" requires at least a path')
    return result


def dict_merge(*dicts, **others):

    '''Merges several dicts into a single one.

    Merging is similar to updating a dict, but if values are non-scalars they
    are also merged is this way:

    - Any two :class:`sequences <collection.Sequence>` or :class:`sets
      <collections.Set>` are joined together.

    - Any two mappings are recursively merged.

    - Other types are just replaced like in :func:`update`.

    If for a single key two values of incompatible types are found, raise a
    TypeError.  If the values for a single key are compatible but different
    (i.e a list an a tuple) the resultant type will be the type of the first
    apparition of the key, unless for mappings which are always cast to dicts.

    No matter the types of `dicts` the result is always a dict.

    Without arguments, return the empty dict.

    '''
    from collections import Mapping, Sequence, Set
    from six import iteritems as iteritems_
    from xoutil.objects import get_first_of
    from xoutil.types import are_instances, no_instances
    if others:
        dicts = dicts + (others, )
    dicts = list(dicts)
    result = {}
    collections = (Set, Sequence)
    while dicts:
        current = dicts.pop(0)
        for key, val in iteritems_(current):
            if isinstance(val, Mapping):
                val = {key: val[key] for key in val}
            value = result.setdefault(key, val)
            if value is not val:
                if are_instances(value, val, collections):
                    join = get_first_of((value, ), '__add__', '__or__')
                    if join:
                        constructor = type(value)
                        value = join(constructor(val))
                    else:
                        raise ValueError("Invalid value for key '%s'"
                                         % key)
                elif are_instances(value, val, Mapping):
                    value = dict_merge(value, val)
                elif no_instances(value, val, (Set, Sequence, Mapping)):
                    value = val
                else:
                    raise TypeError("Found incompatible values for key '%s'"
                                    % key)
                result[key] = value
    return result
