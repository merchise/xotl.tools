# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.future.types
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~] and Contributors
# Copyright (c) 2010-2012 Medardo Rodriguez
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Migrated to 'future' on 2016-09-12

'''Extends the standard `types` module.

Standard module defines names for all type symbols known in the standard
interpreter.

This modules mirrors all the functions (and, in general, objects) from the
standard library module `types`:mod:; but it also includes several new types
and type-related functions.

This module unifies old `xoutil.types`:mod: and `xoutil.eigth.types`:mod:
modules, which are deprecated now.

There are some symbols included in Python 2.x series, but not in Python 3 that
we don't include here:

- `TypeType`: use `type` instead

- `ObjectType`: use `object`

- `IntType`: use `int`

- `LongType`: use `long` in Python 2 and `int` in Python 3; better see
  `xoutil.eight.integer_types` definition.

- `FloatType`: use `float`

- `BooleanType`: use `bool`

- `ComplexType`: use `complex`

- `StringType`: use str

- `UnicodeType`: use `unicode` in Python 2 and `str` in Python 3; there are
  two aliases for that: `xoutil.eigth.UnicodeType` and
  `xoutil.eigth.text_type`.

- `StringTypes`: use `xoutil.eigth.StringTypes`or
  `xoutil.eigth.string_types`.

- `BufferType`: use `buffer` in Python 2 and `memoryview` in Python 3; there
  is an alias for this convention in `xoutil.eigth.buffer`.  The
  `memoryview`:class: API is similar but not exactly the same as that of
  `buffer`.

- `TupleType`: use `tuple`

- `ListType`: use `list`

- `DictType` (or `DictionaryType`): use `dict`

- `ClassType`: Python 2 old-style classes, don't exists in Python 3, see
  `xoutil.eigth.ClassTypes`.

- `InstanceType`: type of instances of Python 2 old-style classes, don't
  exists in Python 3, see `xoutil.eigth.typeof`.

- `UnboundMethodType`: use `~types.MethodType` alias

- `FileType`: use `file`

- `XRangeType` (or `xrange`): in Python 3 `range` always returns a generator
  object; use `xoutil.eigth.range`:class: for compatibility; wraps it with
  list (``list(range(...))``) to obtain old `range` style

- `SliceType`: use `slice`

- In Jython and PyPy, `MemberDescriptorType` is identical to
  `GetSetDescriptorType`; to mantain compatibility in some `xoutil` code, they
  are differentiated in this module.

- `CoroutineType` and `coroutine`: use new Python 3 `async` statement; not
  implementable in Python 2.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from types import *    # noqa
import types as _stdlib    # noqa

from xoutil.deprecation import deprecate_linked
deprecate_linked()
del deprecate_linked

from xoutil.eight import python_version    # noqa

try:
    from types import __all__    # noqa
    __all__ = list(__all__)
except ImportError:
    # Python 3.3 don't implement '__all__' for 'string' module.
    __all__ = [name for name in dir(_stdlib) if not name.startswith('_')]

try:
    NoneType    # noqa
except NameError:
    NoneType = type(None)
    __all__.append('NoneType')

try:
    EllipsisType    # noqa
except NameError:
    EllipsisType = type(Ellipsis)
    __all__.append('EllipsisType')

try:
    DictProxyType    # noqa
except NameError:
    DictProxyType = type(type.__dict__)
    __all__.append('DictProxyType')

try:
    MappingProxyType    # noqa
except NameError:
    from xoutil.eight._types import MappingProxyType
    if MappingProxyType is not DictProxyType:
        MappingProxyType.register(DictProxyType)
    __all__.append('MappingProxyType')

if python_version == 2:
    from collections import Mapping
    if not issubclass(MappingProxyType, Mapping):
        # TODO: when implement `xoutil.future.collections`, fix this problem
        # there.
        Mapping.register(MappingProxyType)
    del Mapping

try:
    NotImplementedType    # noqa
except NameError:
    NotImplementedType = type(NotImplemented)
    __all__.append('NotImplementedType')


# Check Jython and PyPy peculiarity
if MemberDescriptorType is GetSetDescriptorType:    # noqa
    class _foo(object):
        __slots__ = 'bar'
    MemberDescriptorType = type(_foo.bar)
    del _foo

FuncTypes = tuple({FunctionType, MethodType, LambdaType,    # noqa
                   BuiltinFunctionType, BuiltinMethodType})    # noqa

from xoutil.eight import class_types    # noqa
func_types = FuncTypes    # Just an alias

# These types are defined in `inspect` module for Python >= 3.3
MethodWrapperType = type(all.__call__)
WrapperDescriptorType = type(type.__call__)    # In PyPy is MethodWrapperType
ClassMethodWrapperType = type(dict.__dict__['fromkeys'])


sn_ok = python_version >= 3.4
if sn_ok:
    try:
        SimpleNamespace    # noqa
    except NameError:
        sn_ok = False
        __all__.append('SimpleNamespace')

if not sn_ok:
    from abc import ABCMeta
    from xoutil.eight.meta import metaclass

    from xoutil.reprlib import recursive_repr

    class SimpleNamespace(metaclass(ABCMeta)):
        '''A simple attribute-based namespace.

        SimpleNamespace(**kwargs)

        '''

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

        def __eq__(self, other):
            # TODO: This method is not implemented in py33
            ok = isinstance(other, SimpleNamespace)
            return ok and self.__dict__ == other.__dict__

        @recursive_repr(str('namespace(...)'))
        def __repr__(self):
            keys = sorted(self.__dict__)
            items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
            return "{}({})".format('namespace', ", ".join(items))

    del recursive_repr, ABCMeta, metaclass

    try:
        from types import SimpleNamespace as _sns
        # TODO: @manu, why needed in this case?
        SimpleNamespace.register(_sns)
        del _sns
    except ImportError:
        pass

try:
    DynamicClassAttribute    # noqa
except NameError:
    # TODO: Add tests
    class DynamicClassAttribute(property):
        '''Route attribute access on a class to `~object.__getattr__`:meth:.

        This is a descriptor, used to define attributes that act differently
        when accessed through an instance and through a class.  Instance
        access remains normal, but access to an attribute through a class will
        be routed to the class's `~object.__getattr__`:meth: method;
        this is done by raising `AttributeError`:class:.

        This allows one to have properties active on an instance, and have
        virtual attributes on the class with the same name (see
        `~py3:enum.Enum`:class: for an example).

        .. versionadded:: 1.5.5

        .. versionchanged:: 1.8.0 Inherits from `property`

        .. note:: The class `Enum` mentioned has not yet been back-ported.

        .. note:: In Python version>=3.4 this is an alias to
                  `types.DynamicClassAttribute
                  <py3:types.DynamicClassAttribute>`:class:.

        '''
        def __init__(self, fget=None, fset=None, fdel=None, doc=None):
            super(DynamicClassAttribute, self).__init__(fget, fset, fdel, doc)
            # support for abstract methods in Python 2
            isabs = bool(getattr(fget, '__isabstractmethod__', False))
            self.__isabstractmethod__ = isabs

        def __get__(self, obj, owner=None):
            if obj is None:
                if self.__isabstractmethod__:
                    return self
                else:
                    raise AttributeError()
            else:
                return super(DynamicClassAttribute, self).__get__(obj, owner)

    __all__.append('DynamicClassAttribute')

try:
    new_class    # noqa
except NameError:
    from xoutil.eight._types import new_class    # noqa
    __all__.append('new_class')

try:
    prepare_class    # noqa
except NameError:
    from xoutil.eight._types import prepare_class    # noqa
    __all__.append('prepare_class')

try:
    from types import _calculate_meta
except ImportError:
    from xoutil.eight._types import _calculate_meta    # noqa

if __name__ == 'xoutil.types':
    from xoutil.deprecation import deprecated
    from xoutil.symbols import Unset as _unset
    from collections import Mapping
    from xoutil.eight import force_type as type_coerce

    # TODO: @manu, consider for future types
    from re import compile as _regex_compile
    RegexPattern = type(_regex_compile(''))
    del _regex_compile

    # TODO: used internally in this module
    class mro_dict(Mapping):
        '''Utility behaving like a read-only dict of `target` MRO attributes.

        For example::

          >>> class A(object):
          ...     x = 12
          ...     y = 34

          >>> class B(A):
          ...     y = 56
          ...     z = 78

          >>> d = mro_dict(B)

          >>> d['x']
          12

          >>> d['y']
          56

          >>> d['z']
          78

        '''
        # TODO: What is the application for this utility?
        __slots__ = ('_probes', '_keys')

        def __init__(self, target):
            from xoutil.future.inspect import _static_getmro
            type_ = type_coerce(target)
            target_mro = _static_getmro(type_)
            self._probes = tuple(c.__dict__ for c in target_mro)
            self._keys = set()

        def __getitem__(self, name):
            from xoutil.objects import get_first_of
            result = get_first_of(self._probes, name, default=_unset)
            if result is not _unset:
                return result
            else:
                raise KeyError(name)

        def __iter__(self):
            if not self._keys:
                self._settle_keys()
            return iter(self._keys)

        def __len__(self):
            if not self._keys:
                self._settle_keys()
            return len(self._keys)

        def _settle_keys(self):
            for probe in self._probes:
                for key in probe:
                    if key not in self._keys:
                        self._keys.add(key)

    # TODO: used internally in this module
    def mro_get_value_list(cls, name):
        '''Return a list with all `cls` class attributes in MRO.'''
        from xoutil.future.inspect import _static_getmro
        mro = _static_getmro(type_coerce(cls))
        return [t.__dict__[name] for t in mro if name in t.__dict__]

    # TODO: not further use
    def mro_get_full_mapping(cls, name):
        '''Return a dictionary with all items from `cls` in MRO.

        All values corresponding to `name` must be valid mappings.

        '''
        aux = mro_get_value_list(cls, name)
        count = len(aux)
        if count == 0:
            return {}
        elif count == 1:
            return aux[0]
        else:
            res = {}
            for m in aux:
                for key in m:
                    if key not in res:
                        res[key] = m[key]
            return res

    # TODO: Many of is_*method methods here are needed to be compared against
    # the standard lib's module inspect versions.  If they behave the same,
    # these should be deprecated in favor of the standards.

    # TODO: use in `xoutil.json.JSONEncoder` was replaced by
    # ``isinstance(maybe, Iterable)``, so now is used only internally.
    def is_iterable(maybe):
        '''Returns True if `maybe` is an iterable object (e.g. implements the
        `__iter__` method):

        ::

            >>> is_iterable('all strings are iterable')
            True

            # Numbers are not
            >>> is_iterable(1)
            False

            >>> from xoutil.eight import range
            >>> is_iterable(range(1))
            True

            >>> is_iterable({})
            True

            >>> is_iterable(tuple())
            True

            >>> is_iterable(set())
            True

        '''
        try:
            iter(maybe)
        except:
            return False
        else:
            return True

    # TODO: @manu, external uses to be upgraded:
    #
    # - `odoo.addons.mail.xopgi.index`: can be replaced by a local function
    #   ``isinstance(maybe, (tuple, list, set))`` or by
    #   `xoutil.values.simple.logic_iterable_coerce`.
    #
    # - `xopgi.account.xopgi.xopgi_proper_currency.move`: ibidem
    #
    # - `xopgi.base.xopgi.xopgi_recurrence.models.recurrent_model`: two uses,
    #   the first is similar to above examples, second use the concept of
    #   arrays (mappings are collections but not arrays) and maybe must
    #   consider to move this function to new `xoutil.future.collections` and
    #   use it from there.  @med, consider
    #   `xoutil.values.simple.array_coerce`.
    #
    # - `xopgi.hr.xopgi.xopgi_hr_job_assets.hr_job`: ibidem to first.
    #
    # - `xopgi.hr_contract.xopgi.xopgi_hr_contract.hr_contract`: ibidem.
    #
    # - `xequiotl.rstmodel`: ibidem.
    #
    # - `xoeuf.cli.mailgate`: ibidem.
    #
    # - `xoeuf.cli.secure`: ibidem.
    #
    # - `xoeuf.osv.model_extensions`: ibidem.
    #
    # - `xoeuf.osv.writers`: ibidem.
    #
    # - `xotl.simple.event`: ibidem.
    #
    # - `xoutil.tests.test_types`: reconfigure all tests after upgrading all
    #   uses.
    #
    # - `xoutil.cpystack`: migrated to use new
    #   `xoutil.values.simple.force_sequence_coerce`.
    #
    # - `xoutil.fs`: migrated to use
    #    `xoutil.values.simple.force_iterable_coerce`.
    #
    # - `xoutil.iterators`: replaced by ``isinstance(fill, Iterable)``.
    #
    # - `xoutil.objects`: replaced by
    #   `xoutil.values.simple.logic_collection_coerce` or
    #   `xoutil.values.simple.logic_iterable_coerce`.
    def is_collection(maybe):
        '''Test `maybe` to see if it is a tuple, a list, a set or a generator
        function.

        It returns False for dictionaries and strings::

            >>> is_collection('all strings are iterable')
            False

            # Numbers are not
            >>> is_collection(1)
            False

            >>> from xoutil.eight import range
            >>> is_collection(range(1))
            True

            >>> is_collection({})
            False

            >>> is_collection(tuple())
            True

            >>> is_collection(set())
            True

            >>> is_collection(a for a in range(100))
            True

        .. versionchanged:: 1.5.5 UserList are collections.

        '''
        from xoutil.values.simple import logic_collection_coerce, nil
        return logic_collection_coerce(maybe) is not nil

    # TODO: There was only one reference to this in `xoutil.objects`, see how
    # was replaced in the new body of this function
    def is_mapping(maybe):
        '''Test `maybe` to see if it is a valid mapping.'''
        from xoutil.future.collections import Mapping
        return isinstance(maybe, Mapping)

    # only referenced locally by `is_scalar`.
    def is_string_like(maybe):
        '''Returns True if `maybe` acts like a string'''
        try:
            maybe + ""
        except TypeError:
            return False
        else:
            return True

    # TODO: @manu, @med, review external references to this function, and
    # remove them:
    #
    # - `xoonko.core.management.profiles.loaders.models_loader`
    #
    # - `xoonko.core.management.profiles.producers.json_producer`
    #
    # - `xoutil.iterators`
    def is_scalar(maybe):
        '''Returns True if `maybe` is a string, an int, or some other scalar type
        (i.e not an iterable.)

        '''
        return is_string_like(maybe) or not is_iterable(maybe)

    # TODO: @manu, @med, review external references to this function, and
    # remove them:
    #
    # - `xoutil.objects`: only a reference in a comment, must be removed.
    #
    # - `xoutil.records`: fixed.
    def is_staticmethod(desc, name=_unset):
        '''Returns true if a `method` is a static method.

        This function takes the same arguments as `is_classmethod`:func:.

        '''
        if name:
            desc = mro_dict(desc).get(name, None)
        return isinstance(desc, staticmethod)

    # TODO: @manu, @med, review external references to this function, and
    # remove them:
    #
    # - `xoutil.objects`: only a reference in a comment, must be removed.
    def is_classmethod(desc, name=_unset):
        '''Returns true if a `method` is a class method.

        :param desc: This may be the method descriptor or the class that holds
               the method, in the second case you must provide the `name` of
               the method.

               .. note::

                  Notice that in the first case what is needed is the **method
                  descriptor**, i.e, taken from the class' `__dict__`
                  attribute. If instead you pass something like
                  ``cls.methodname``, this method will return False whilst
                  `is_instancemethod`:func: will return True.

        :param name: The name of the method, if the first argument is the
               class.

        '''
        if name:
            desc = mro_dict(desc).get(name, None)
        return isinstance(desc, classmethod)

    # not used outside this module.
    def is_instancemethod(desc, name=_unset):
        '''Returns true if a given `method` is neither a static method nor a class
        method.

        This function takes the same arguments as `is_classmethod`:func:.

        '''
        if name:
            desc = mro_dict(desc).get(name, None)
        return isinstance(desc, FunctionType)    # noqa

    # not used outside this module.
    def is_module(maybe):
        '''Returns True if `maybe` is a module.'''
        return isinstance(maybe, ModuleType)    # noqa

    # TODO: @manu, @med, review external references to this function, and
    # remove them:
    #
    # - `xoutil.objects.smart_copy`.
    @deprecated(type(_unset), 'This is only used in `~objects.smart_copy`.')
    class Required(object):
        '''A type for required fields in scenarios where a default is not
        possible.

        '''
        def __init__(self, *args, **kwargs):
            pass

    # TODO: @manu, @med, review external references to this function, and
    # remove them:
    #
    # - `xopgi_recurrence.models.recurrent_model`: sentence
    #   ``are_instances(leftres, rightres, tuple)`` must be replaced by
    #   ``isinstance(leftres, tuple) and isinstance(rightres, tuple)``.
    #
    # - `xoutil.objects`
    #
    # Real "Py4k" signature ``are_instances(*subjects, types)``.
    def are_instances(*args):
        '''Return True if every `subject` is an instance of (any) `types`.

        :param subjects: All but last positional arguments.  Are the objects
            required to be instances of `types`.

        :param types: The last positional argument.  Either a single type or a
           sequence of types.  This must meet the conditions on the last
           argument of `isinstance`:func:.

        :returns: True or False.  True if for every `subject`,
           ``isinstance(subject, types)`` is True.  Otherwise, False.

        If no `subjects` are provided return True::

            >>> are_instances(int)
            True

        .. seealso:: The function `no_instances`:func: allows to test for
                     subjects not being instances of types.

        '''
        from xoutil.params import check_count
        check_count(args, 1, caller='are_instances')
        subjects, types = args[:-1], args[-1]
        if not subjects:
            isinstance(None, types)   # HACK: always validate `types`.
        return all(isinstance(subject, types) for subject in subjects)

    # TODO: @manu, @med, review external references to this function, and
    # remove them:
    #
    # - `xoutil.objects`
    #
    # Real Py4k signature ``are_instances(*subjects, types)``self.
    def no_instances(*args):
        '''Return True if every `subject` is **not** an instance of (neither)
        `types`.

        :param subjects: All but last positional arguments.  Are the objects
               required not to be instances of `types`.

        :param types: The last positional argument.  Either a single type or a
               sequence of types.  This must meet the conditions on the last
               argument of `isinstance`:func:.

        :returns: True or False.  True if for every `subject`,
                  ``isinstance(subject, types)`` is False.  Otherwise, False.

        If no `subjects` are provided return True::

            >>> no_instances(int)
            True

        .. note:: This is not the same as ``not are_instances(...)``.

           This function requires that *no* subject is an instance of `types`.
           Negating `are_instances`:func: would be True if *any* subject is
           not an instance of `types`.

        '''
        from xoutil.params import check_count
        check_count(args, 1, caller='no_instances')
        subjects, types = args[:-1], args[-1]
        if not subjects:
            isinstance(None, types)   # HACK: always validate `types`.
        return all(not isinstance(subject, types) for subject in subjects)

    del deprecated
