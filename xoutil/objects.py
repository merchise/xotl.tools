#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Several utilities for objects in general.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from contextlib import contextmanager

from xoutil.symbols import Unset
from xoutil.deprecation import deprecated


__docstring_format__ = 'rst'


_INVALID_CLASS_TYPE_MSG = '``cls`` must be a class not an instance'


def _len(x):
    'Safe length'
    return len(x) if x else 0


# TODO: Deprecate these two functions, can be used to always return True or
# False
def _true(*args, **kwargs):
    return True


def _false(*args, **kwargs):
    return False


class SafeDataItem(object):
    '''A data descriptor that is safe.

    A *safe descriptor* never uses internal special methods ``__getattr__``
    and ``__getattribute__`` to obtain its value.  Also allow to define a
    constructor or a default value for the first time the attribute is read
    without a prior value assigned.

    Need to be used only in scenarios where descriptor instance values must be
    accessed safely in '__getattr__' implementations.

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

        - A checker for value validity with the keyword argument with any of
          the following names: `validator`, `checker` or `check`.  The checker
          could be a type, a tuple of types, a function receiving the value
          and return True or False, or a list containing arguments to use
          `xoutil.validators.check`:func:.

        - Boolean `False` to avoid assigning the descriptor in the class
          context with the keyword argument `do_assigning`.  Any other value
          but `False` is invalid because this concept is implicitly required
          and use a `False` value is allowed but discouraged.

        See :meth:`__parse_arguments` for more information.

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
            IN_FUNC_TYPES = FUNC_KINDS.__contains__
            KIND_NAME = 'kind'
            kind = kwargs.pop(KIND_NAME, FUNC_KINDS[0])
            if check(kind, IN_FUNC_TYPES) and check(method, FUNC_TYPES):
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
            from xoutil.future.inspect import get_attr_value
            res = get_attr_value(obj, self.inner_name, Unset)
            if res is not Unset:
                return res
            elif self.init is not Unset:
                res = self.init()
                self.__set__(obj, res)
                return res
            elif self.default is not Unset:
                res = self.default
                self.__set__(obj, res)
                return res
            else:
                from xoutil.eight import type_name
                msg = "'%s' object has no attribute '%s'"
                raise AttributeError(msg % (type_name(obj), self.attr_name))
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
        return '_%s' % int2str(int(1000000 * time()))

    def __parse_arguments(self, *args, **kwargs):
        '''Assign parsed arguments to the just created instance.'''
        from xoutil.eight import callable
        from xoutil.validators import (is_valid_identifier, predicate)
        self.attr_name = Unset
        self.init = Unset
        self.default = Unset
        self.do_assigning = True
        self.validator = True
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
            elif (self.validator is True and
                  key in ('validator', 'checker', 'check')):
                self.validator = value
            elif (self.do_assigning is True and key == 'do_assigning' and
                  value is False):
                self.do_assigning = False
            else:
                bads[key] = value
        self.validator = predicate(self.validator)
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

    If `obj` is a mapping, it returns the ``.get()`` method bound to the
    object `obj`, otherwise it returns a partial of ``getattr`` on `obj`.

    :param strict: Set this to True so that the returned getter checks that
                   keys/attrs exists.  If `strict` is True the getter may
                   raise a KeyError or an AttributeError.

    .. versionchanged:: 1.5.3 Added the parameter `strict`.

    '''
    from xoutil.future.collections import Mapping
    if isinstance(obj, Mapping):
        if not strict:
            return obj.get
        else:
            def getter(key, default=Unset):
                "Get the given key. Raise an error when it doesn't exists."
                try:
                    return obj[key]
                except KeyError:
                    if default is Unset:
                        raise
                    else:
                        return default
            return getter
    else:
        if not strict:
            def getter(attr, default=None):
                "Get the given attr. Return default if it doesn't exists."
                return getattr(obj, attr, default)
            return getter
        else:
            def getter(attr, default=Unset):
                "Get the given attr. Raise an error when it doesn't exists."
                try:
                    return getattr(obj, attr)
                except AttributeError:
                    if default is Unset:
                        raise
                    else:
                        return default
            return getter


def smart_setter(obj):
    '''Returns a smart setter for `obj`.

    If `obj` is a mutable mapping, it returns the ``.__setitem__()`` method
    bound to the object `obj`, otherwise it returns a partial of ``setattr``
    on `obj`.

    .. versionadded:: 1.8.2

    '''
    from xoutil.future.functools import partial
    from xoutil.future.collections import MutableMapping
    if isinstance(obj, MutableMapping):
        return obj.__setitem__
    else:
        return partial(setattr, obj)


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


# TODO: [med] See the get_traverser.  I think the function is actually
# a subtype of that.  Also, this method sticks with the getter for the
# top object, see the failing companion test in this commit.
def multi_getter(source, *ids):
    '''Get values from `source` of all given `ids`.

    :param source: Any object but dealing with differences between mappings
           and other object types.

    :param ids: Identifiers to get values from `source`.

           An ID item could be:

           - a string: is considered a key, if `source` is a mapping, or an
             attribute name if `source` is an instance of any other type.

           - a collection of strings: find the first valid value in `source`
             evaluating each item in this collection using the above logic.

    Example::

      >>> d = {'x': 1, 'y': 2, 'z': 3}
      >>> list(multi_getter(d, 'a', ('y', 'x'), ('x', 'y'), ('a', 'z', 'x')))
      [None, 2, 1, 3]

      >>> next(multi_getter(d, ('y', 'x'), ('x', 'y')), '---')
      2

      >>> next(multi_getter(d, 'a', ('b', 'c'), ('e', 'f')), '---') is None
      True

    .. versionadded:: 1.7.1

    '''
    getter = smart_getter(source)

    def first(a):
        return next((i for i in map(getter, a) if i is not None), None)

    def get(a):
        from xoutil.values.simple import logic_iterable_coerce as many
        return first(a) if many(a) else getter(a)

    return (get(aux) for aux in ids)


def mass_setattr(obj, **attrs):
    '''Set all given attributes and return the same object.'''
    # See 'xoutil.decorator.constant_bagger' ;)
    for attr in attrs:
        setattr(obj, attr, attrs[attr])
    return obj


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


# TODO: @med, @manu, Decide if it's best to create a 'xoutil.future.inspect'
# that extends the standard library module 'inspect' and place this
# signature-dealing functions there.  Probably, to be consistent, this imposes
# a refactoring of some of 'xoutil.future.types' and move all the
# "is_classmethod", "is_staticmethod" and inspection-related functions there.
def get_method_function(cls, method_name):
    '''Get definition function given in its `method_name`.

    There is a difference between the result of this function and
    ``getattr(cls, method_name)`` because the last one return the unbound
    method and this a python function.

    '''
    from xoutil.eight import callable
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
    '''Build a proper documentation from a class `cls`.

    Classes are recursed in MRO until process all levels (`deep`)
    building the resulting documentation.

    The function `get_doc` get the documentation of a given class. If
    no function is given, then attribute ``__doc__`` is used.

    '''
    from xoutil.future.codecs import safe_decode
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

    If `cls` has an invalid documentation, super-classes are recursed
    in MRO until a documentation definition was made at any level.

    :param ignore: could be used to specify which classes to ignore by
                   specifying its name in this list.

    :param min_length: specify that documentations with less that a number of
                       characters, also are ignored.

    '''
    from xoutil.eight import callable
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

    If `cls` has an invalid documentation, super-classes are recursed in MRO
    until a documentation definition was made at any level.

    :param ignore: could be used to specify which classes to ignore by
                   specifying its name in this list.

    :param min_length: specify that documentations with less that a number of
                       characters, also are ignored.

    '''
    from xoutil.eight import callable
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
    from xoutil.eight import typeof, class_types
    from xoutil.future.inspect import get_attr_value, _static_getmro

    def getdir(o):
        return set(get_attr_value(o, '__dict__', {}))

    if isinstance(obj, class_types):
        res = set.union(getdir(cls) for cls in _static_getmro(obj))
    else:
        res = getdir(obj)
    cls = typeof(obj)
    return res if cls in class_types else res | set(dir(cls))


def xdir(obj, getter=None, filter=None, _depth=0):
    '''Return all ``(attr, value)`` pairs from `obj` make ``filter(attr, value)``
    True.

    :param obj: The object to be instrospected.

    :param filter: A filter that will be passed both the attribute
       name and it's value as two positional arguments. It should return True
       for attrs that should be yielded.

       If None, all pairs will match.

    :param getter: A function with the same signature that
                   ``getattr`` to be used to get the values from `obj`.  If
                   None, use `getattr`:func:.

    .. versionchanged:: 1.8.1 Removed deprecated `attr_filter` and
       `value_filter` arguments.

    '''
    getter = getter or getattr
    attrs = dir(obj)
    res = ((a, getter(obj, a)) for a in attrs)
    if filter:
        res = ((a, v) for a, v in res if filter(a, v))
    return res


def fdir(obj, getter=None, filter=None):
    '''Similar to `xdir`:func: but yields only the attributes names.'''
    full = xdir(obj, getter=getter, filter=filter, _depth=1)
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
    tests = ((eq, force_equals), (ne, force_differents))
    j = 0
    get_from_source = smart_getter(source)
    get_from_target = smart_getter(target)
    while res and (j < len(tests)):
        passed, attrs = tests[j]
        i = 0
        while res and (i < len(attrs)):
            attr = attrs[i]
            if passed(get_from_source(attr), get_from_target(attr)):
                i += 1
            else:
                res = False
        j += 1
    return res


# Mark this so that informed people may use it.
validate_attrs._positive_testing = True


def iterate_over(source, *keys):
    '''Yields pairs of (key, value) for of all `keys` in `source`.

    If any `key` is missing from `source` is ignored (not yielded).

    If `source` is a `collection
    <xoutil.values.simple.logic_collection_coerce>`:func:, iterate over each
    of the items searching for any of keys.  This is not recursive.

    If no `keys` are provided, return an "empty" iterator -- i.e will raise
    StopIteration upon calling `next`.

    .. versionadded:: 1.5.2

    '''
    from xoutil.values.simple import logic_collection_coerce, nil

    def inner(source):
        get = smart_getter(source)
        for key in keys:
            val = get(key, Unset)
            if val is not Unset:
                yield key, val

    def when_collection(source):
        from xoutil.future.itertools import map
        for generator in map(inner, source):
            for key, val in generator:
                yield key, val

    if logic_collection_coerce(source) is not nil:
        res = when_collection(source)
    else:
        res = inner(source)
    return res


def get_first_of(source, *keys, **kwargs):
    '''Return the value of the first occurrence of any of the specified `keys`
    in `source` that matches `pred` (if given).

    Both `source` and `keys` has the same meaning as in `iterate_over`:func:.

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
    '''Similar to `get_first_of`:func: using as `source` either an object or a
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
    from xoutil.values.simple import logic_collection_coerce, nil

    def inner(source):
        get = smart_getter_and_deleter(source)
        res, i = Unset, 0
        while (res is Unset) and (i < len(keys)):
            res = get(keys[i], Unset)
            i += 1
        return res

    if logic_collection_coerce(source) is not nil:
        res = Unset
        source = iter(source)
        probe = next(source, None)
        while res is Unset and probe:
            res = inner(probe)
            probe = next(source, None)
    else:
        res = inner(source)
    return res if res is not Unset else kwargs.get('default', None)


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


class lazy(object):
    '''Marks a value as a lazily evaluated value. See `setdefaultattr`:func:.

    '''
    def __init__(self, value, *args, **kwargs):
        self.value = value
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        from xoutil.eight import callable
        res = self.value
        if callable(res):
            return res(*self.args, **self.kwargs)
        else:
            return res


def iter_branch_subclasses(cls, include_this=True):
    '''Internal function, see `get_branch_subclasses`:func:.'''
    children = type.__subclasses__(cls)
    if children:
        for sc in children:
            for item in iter_branch_subclasses(sc):
                yield item
    elif include_this:
        yield cls


def get_branch_subclasses(cls):
    '''Similar to `type.__subclasses__`:meth: but recursive.

    Only return sub-classes in branches (those with no sub-classes).  Instead
    of returning a list, yield each valid value.

    .. versionadded:: 1.7.0

    '''
    return list(iter_branch_subclasses(cls, include_this=False))


# TODO: Check `xoutil.future.types.DynamicClassAttribute`:class: for more
# information and to compare with this one.
class xproperty(property):
    '''Descriptor that gets values the same for instances and for classes.

    Example of its use::

        >>> class Foobar(object):
        ...     _x = 'in the class'
        ...
        ...     def __init__(self):
        ...         self._x = 'in the instance'
        ...
        ...     @xproperty
        ...     def x(self):
        ...         return self._x

        >>> f = Foobar()

        >>> Foobar.x
        'in the class'

        >>> f.x
        'in the instance'

    X-properties are always read-only, if attribute values must be set or
    deleted, a metaclass must be defined.

    .. versionadded:: 1.8.0

    '''
    def __init__(self, fget, doc=None):
        if fget is not None:
            super(xproperty, self).__init__(fget, doc=doc)
        else:
            raise TypeError('xproperty() the "fget" argument is requiered')

    def __get__(self, instance, owner):
        return self.fget(instance if instance is not None else owner)


class classproperty(property):
    '''A descriptor that behaves like property for instances but for classes.

    Example of its use::

        class Foobar(object):
            @classproperty
            def getx(cls):
                return cls._x

    A writable `classproperty` is difficult to define, and it's not intended
    for that case because 'setter', and 'deleter' decorators can't be used for
    obvious reasons.  For example::

        class Foobar(object):
            x = 1
            def __init__(self, x=2):
                self.x = x
            def _get_name(cls):
                return str(cls.x)
            def _set_name(cls, x):
                cls.x = int(x)
            name = classproperty(_get_name, _set_name)

    .. versionadded:: 1.4.1

    .. versionchanged:: 1.8.0 Inherits from `property`

    '''
    def __get__(self, instance, owner):
        obj = type(instance) if instance is not None else owner
        return super(classproperty, self).__get__(obj, owner)

    def __set__(self, instance, value):
        obj = instance if isinstance(instance, type) else type(instance)
        super(classproperty, self).__set__(obj, value)

    def __delete__(self, instance):
        obj = instance if isinstance(instance, type) else type(instance)
        super(classproperty, self).__delete__(obj)


class staticproperty(property):
    '''A descriptor that behaves like properties for instances but static.

    Example of its use::

        class Foobar(object):
            @staticproperty
            def getx():
                return 'this is static'

    A writable `staticproperty` is difficult to define, and it's not intended
    for that case because 'setter', and 'deleter' decorators can't be used for
    obvious reasons.  For example::

        class Foobar(object):
            x = 1
            def __init__(self, x=2):
                self.x = x
            def _get_name():
                return str(Foobar.x)
            def _set_name(x):
                Foobar.x = int(x)
            name = staticproperty(_get_name, _set_name)

    .. versionadded:: 1.8

    '''
    def __get__(self, instance, owner):
        if self.fget is not None:
            return self.fget()
        else:
            raise AttributeError('unreadable attribute')

    def __set__(self, instance, value):
        if self.fset is not None:
            self.fset(value)
        else:
            raise AttributeError("can't set attribute")

    def __delete__(self, instance):
        if self.fdel is not None:
            self.fdel()
        else:
            raise AttributeError("can't delete attribute")


# The following is extracted from the SQLAlchemy project's codebase, merit and
# copyright goes to SQLAlchemy authors.
#
# Copyright (C) 2005-2011 the SQLAlchemy authors and contributors
#
# This module is part of SQLAlchemy and is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php
#
class memoized_property(object):
    """A read-only property that is only evaluated once.

    This is extracted from the SQLAlchemy project's codebase, merit and
    copyright goes to SQLAlchemy authors::

      Copyright (C) 2005-2011 the SQLAlchemy authors and contributors

      This module is part of SQLAlchemy and is released under the MIT License:
      http://www.opensource.org/licenses/mit-license.php

    """
    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        obj.__dict__[self.__name__] = result = self.fget(obj)
        return result

    def reset(self, instance):
        '''Clear the cached value of `instance`.'''
        instance.__dict__.pop(self.__name__, None)


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


def adapt_exception(value, **kwargs):
    '''Like PEP-246, Object Adaptation, with ``adapt(value, Exception,
    None)``.

    If the value is not an exception is expected to be a tuple/list which
    contains an Exception type as its first item.

    .. versionchanged:: 1.8.0 Moved from `xoutil.data`:mod: module.

    '''
    isi, ebc = isinstance, Exception    # TODO: Maybe must be `BaseException`
    issc = lambda maybe, cls: isi(maybe, type) and issubclass(maybe, cls)
    if isi(value, ebc) or issc(value, ebc):
        return value
    elif isi(value, (tuple, list)) and len(value) > 0 and issc(value[0], ebc):
        from xoutil.eight import string_types as strs
        map = lambda x: x.format(**kwargs) if isinstance(x, strs) else x
        ecls = value[0]
        return ecls(*(map(x) for x in value[1:]))
    else:
        return None


def copy_class(cls, meta=None, ignores=None, new_attrs=None, new_name=None):
    '''Copies a class definition to a new class.

    The returned class will have the same name, bases and module of `cls`.

    :param meta: If None, the `type(cls)` of the class is used to build the
                 new class, otherwise this must be a *proper* metaclass.

    :param ignores: A sequence of attributes names that should not be copied
        to the new class.

        An item may be callable accepting a single argument `attr` that must
        return a non-null value if the the `attr` should be ignored.

    :param new_attrs: New attributes the class must have. These will take
                      precedence over the attributes in the original class.

    :type new_attrs: dict

    :param new_name: The name for the copy.  If not provided the name will
                     copied.

    .. versionadded:: 1.4.0

    .. versionchanged:: 1.7.1 The `ignores` argument must an iterable of
       strings or callables.  Removed the glob-pattern and regular expressions
       as possible values.  They are all possible via the callable variant.

    .. versionadded:: 1.7.1 The `new_name` argument.

    '''
    from xoutil.eight import iteritems, callable
    from xoutil.eight._types import new_class
    from xoutil.future.types import MemberDescriptorType
    from xoutil.eight import string

    def _get_ignored(what):
        if callable(what):
            return what
        else:
            return lambda s: s == what

    if not meta:
        meta = type(cls)
    if ignores:
        ignores = tuple(_get_ignored(i) for i in ignores)
        ignored = lambda name: any(ignore(name) for ignore in ignores)
    else:
        ignored = None
    valid_names = ('__class__', '__mro__', '__name__', '__weakref__',
                   '__dict__')
    attrs = {name: value
             for name, value in iteritems(cls.__dict__)
             if name not in valid_names
             # Must remove member descriptors, otherwise the old's class
             # descriptor will override those that must be created here.
             if not isinstance(value, MemberDescriptorType)
             if ignored is None or not ignored(name)}
    if new_attrs:
        attrs.update(new_attrs)
    def exec_body(ns):  # noqa: E306 new-line before def
        ns.update(attrs)
    if new_name:
        name = string.force(new_name)
    else:
        name = cls.__name__
    result = new_class(name, cls.__bases__, {'metaclass': meta}, exec_body)
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

    - It's the value `~xoutil.symbols.Undefined`:obj:.

    - An exception object

    - A sequence with is first value being a subclass of Exception. In which
      case `adapt_exception`:class: is used.

    In these cases a KeyError is raised if the key is not found in the
    sources.

    If `default` is an iterable and a key is not found in any of the sources,
    None is copied to `target`.

    If `defaults` is a callable then it should receive one positional
    arguments for the current `attribute name` and several keyword arguments
    (we pass ``source``) and return either True or False if the attribute
    should be copied.

    If `defaults` is False (or None) only the attributes that do not start
    with a "_" are copied, if it's True all attributes are copied.

    When `target` is not a mapping only valid Python identifiers will be
    copied.

    Each `source` is considered a mapping if it's an instance of
    `collections.Mapping` or a `MappingProxyType`.

    The `target` is considered a mapping if it's an instance of
    `collections.MutableMapping`.

    :returns: `target`.

    .. versionchanged:: 1.7.0 `defaults` is now keyword only.

    '''
    from xoutil.eight import base_string, type_name, callable
    from xoutil.future.collections import MutableMapping, Mapping
    from xoutil.symbols import Undefined
    from xoutil.validators.identifiers import is_valid_identifier
    from xoutil.values.simple import logic_iterable_coerce, nil
    defaults = kwargs.pop('defaults', False)
    if kwargs:
        raise TypeError('smart_copy does not accept a "%s" keyword argument'
                        % kwargs.keys()[0])
    sources, target = args[:-1], args[-1]
    if not sources:
        raise TypeError('smart_copy() requires at least one source')
    if isinstance(target, (bool, type(None), int, float, base_string)):
        raise TypeError('target should be a mutable object, not '
                        '{}'.format(type_name(target)))
    if isinstance(target, MutableMapping):
        def setter(key, val):
            target[key] = val
    else:
        def setter(key, val):
            if is_valid_identifier(key):
                setattr(target, key, val)
    _mapping = isinstance(defaults, Mapping)
    if _mapping or logic_iterable_coerce(defaults) is not nil:
        for key, val in ((key, get_first_of(sources, key, default=Unset))
                         for key in defaults):
            if val is Unset:
                if _mapping:
                    val = defaults.get(key, None)
                else:
                    val = None
                exc = adapt_exception(val, key=key)
                if exc or val is Undefined:
                    raise KeyError(key)
            setter(key, val)
    else:
        keys = []
        for source in sources:
            get = smart_getter(source)
            items = source if isinstance(source, Mapping) else dir(source)
            for key in items:
                private = isinstance(key, base_string) and key.startswith('_')
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


@deprecated('xoutil.eight.abc.ABCMeta.register')
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
    `smart_getter`:func: over the objects. If provided `getter` should have
    the signature of `getattr`:func:.

    See `get_traverser`:func: if you need to apply the same path(s) to several
    objects.  Actually this is equivalent to::

        get_traverser(path, default=default, sep=sep, getter=getter)(obj)

    '''
    _traverser = get_traverser(path, default=default, sep=sep, getter=getter)
    return _traverser(obj)


def get_traverser(*paths, **kw):
    '''Combines the power of `traverse`:func: with the expectations from both
    `operator.itemgetter`:func: and `operator.attrgetter`:func:.

    :param paths: Several paths to extract.

    Keyword arguments has the same meaning as in `traverse`:func:.

    :returns: A function the when invoked with an `object` traverse the object
              finding each `path`.

    .. versionadded:: 1.5.3

    '''
    from xoutil.params import check_count
    check_count(paths, 1, caller='get_traverser')

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
    else:
        _traversers = tuple(_traverser(path, **kw) for path in paths)

        def _result(obj):
            return tuple(traverse(obj) for traverse in _traversers)

        result = _result
    return result


def dict_merge(*dicts, **others):
    '''Merges several dicts into a single one.

    Merging is similar to updating a dict, but if values are non-scalars they
    are also merged is this way:

    - Any two `sequences <collection.Sequence>`:class: or :class:`sets
      <collections.Set>` are joined together.

    - Any two mappings are recursively merged.

    - Other types are just replaced like in `update`:func:.

    If for a single key two values of incompatible types are found, raise a
    TypeError.  If the values for a single key are compatible but different
    (i.e a list an a tuple) the resultant type will be the type of the first
    apparition of the key, unless for mappings which are always cast to dicts.

    No matter the types of `dicts` the result is always a dict.

    Without arguments, return the empty dict.

    '''
    from collections import Mapping, Sequence, Set, Container
    from xoutil.eight import iteritems
    if others:
        dicts = dicts + (others, )
    dicts = list(dicts)
    result = {}
    collections = (Set, Sequence)
    while dicts:
        current = dicts.pop(0)
        for key, val in iteritems(current):
            if isinstance(val, Mapping):
                val = {key: val[key] for key in val}
            value = result.setdefault(key, val)
            if value is not val:
                if all(isinstance(v, collections) for v in (value, val)):
                    join = get_first_of((value, ), '__add__', '__or__')
                    if join:
                        constructor = type(value)
                        value = join(constructor(val))
                    else:
                        raise ValueError("Invalid value for key '%s'" % key)
                elif all(isinstance(v, Mapping) for v in (value, val)):
                    value = dict_merge(value, val)
                elif all(not isinstance(v, Container) for v in (value, val)):
                    value = val
                else:
                    raise TypeError("Found incompatible values for key '%s'"
                                    % key)
                result[key] = value
    return result


@contextmanager
def save_attributes(obj, *attrs, **kwargs):
    '''A context manager that restores `obj` attributes at exit.

    We deal with `obj`\ 's attributes with `smart_getter`:func: and
    `smart_setter`:func:.  You can override passing keyword `getter` and
    `setter`.  They must take the object and return a callable to get/set the
    its attributes.

    Basic example:

      >>> from xoutil.future.types import SimpleNamespace as new
      >>> obj = new(a=1, b=2)

      >>> with save_attributes(obj, 'a'):
      ...    obj.a = 2
      ...    obj.b = 3

      >>> obj.a
      1

      >>> obj.b
      3

    Depending on the behavior of `getter` and or the object itself, it may be
    an error to get an attribute or key that does not exists.

      >>> getter = lambda o: lambda a: getattr(o, a)
      >>> with save_attributes(obj, 'c', getter=getter):   # doctest: +ELLIPSIS
      ...    pass
      Traceback (...)
      ...
      AttributeError: ...

    Beware, however, that `smart_getter`:func: is non-strict by default and it
    returns None for a non-existing key or attribute.  In this case, we
    attempt to set that attribute or key at exit:

      >>> with save_attributes(obj, 'x'):
      ...   pass

      >>> obj.x is None
      True

    But, then, setting the value may fail:

      >>> obj = object()
      >>> with save_attribute(obj, 'x'):  # doctest: +ELLIPSIS
      ...   pass
      Traceback (...)
      ...
      AttributeError: ...

    .. versionadded:: 1.8.2

    '''
    from xoutil.params import check_count
    check_count(attrs, 1)
    getter = kwargs.get('getter', smart_getter)
    setter = kwargs.get('setter', smart_setter)
    get_ = getter(obj)
    set_ = setter(obj)
    props = {attr: get_(attr) for attr in attrs}
    try:
        yield obj
    finally:
        for attr, val in props.items():
            set_(attr, val)


@contextmanager
def temp_attributes(obj, attrs, **kwargs):
    '''A context manager that temporarily sets attributes.

    `attrs` is a dictionary containing the attributes to set.

    Keyword arguments `getter` and `setter` have the same meaning as in
    `save_attributes`:func:.  We also use the `setter` to set the values
    provided in `attrs`.

    .. versionadded:: 1.8.5

    '''
    setter = kwargs.get('setter', smart_setter)
    set_ = setter(obj)
    with save_attributes(obj, *tuple(attrs.keys()), **kwargs):
        for attr, value in attrs.items():
            set_(attr, value)
        yield


def import_object(name, package=None, sep='.', default=None, **kwargs):
    """Get symbol by qualified name.

    The name should be the full dot-separated path to the class::

        modulename.ClassName

    Example::

        celery.concurrency.processes.TaskPool
                                    ^- class name

    or using ':' to separate module and symbol::

        celery.concurrency.processes:TaskPool

    Examples::

        >>> import_object('celery.concurrency.processes.TaskPool')
        <class 'celery.concurrency.processes.TaskPool'>

        # Does not try to look up non-string names.
        >>> from celery.concurrency.processes import TaskPool
        >>> import_object(TaskPool) is TaskPool
        True

    """
    import importlib
    from xoutil.eight import string_types
    imp = importlib.import_module
    if not isinstance(name, string_types):
        return name                                 # already a class
    sep = ':' if ':' in name else sep
    module_name, _, cls_name = name.rpartition(sep)
    if not module_name:
        cls_name, module_name = None, package if package else cls_name
    try:
        module = imp(module_name, package=package, **kwargs)
        return getattr(module, cls_name) if cls_name else module
    except (ImportError, AttributeError):
        if default is None:
            raise
    return default


def delegator(attribute, attrs_map, metaclass=type):
    '''Create a base class that delegates attributes to another object.

    The returned base class contains a `delegated attribute descriptor
    <DelegatedAttribute>`:class: for each key in `attrs_map`.

    :param attribute: The attribute of the delegating object that holds the
                      delegated attributes.

    :param attrs_map: A map of attributes to delegate.  The keys are the
                      attribute names the delegating object attributes, and
                      the values the attribute names of the delegated object.

    Example:

        >>> class Bar(object):
        ...     x = 'bar'

        >>> class Foo(delegator('egg', {'x1': 'x'})):
        ...     def __init__(self):
        ...         self.egg = Bar()

        >>> foo = Foo()
        >>> foo.x1
        'bar'

    .. versionadded:: 1.9.3

    '''
    descriptors = {
        key: DelegatedAttribute(attribute, attr)
        for key, attr in attrs_map.items()
    }
    return metaclass('delegator', (object, ), descriptors)


class DelegatedAttribute(object):
    '''A delegator data descriptor.

    When accessed the descriptor finds the `delegated_attr` in the instance's
    value given by attribute `target_name`.

    If the instance has no attribute with name `target_name`, raise an
    AttributeError.

    If the target object does not have an attribute with name `delegate_attr`
    and `default` is `~xoutil.symbols.Unset`:data:, raise an AttributeError.
    If `default` is not Unset, return `default`.

    .. versionadded:: 1.9.3

    '''
    def __init__(self, target_name, delegated_attr, default=Unset):
        self.target_name = target_name
        self.attr = delegated_attr
        self.default = default

    def __get__(self, instance, owner):
        if instance is not None:
            target = getattr(instance, self.target_name)
            try:
                return getattr(target, self.attr)
            except AttributeError:
                if self.default is not Unset:
                    return self.default
                else:
                    raise
        else:
            return self

    def __repr__(self):
        return "<DelegatedAttr '%s.%s'>" % (self.target_name, self.attr)


del contextmanager
