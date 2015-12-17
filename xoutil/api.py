#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.api
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-10-19

'''Support the abstraction layer intended for API definitions.

There are two base classes for API definition:

- `Handler`:class:`\ : A base class -or ABC register- that allow to define
  interfaces and tools (in foundation and common layers) representing specific
  driver implementations.

- `Error`:class:`\ : Generic error bases that adopt different shapes in
  specific handler driver implementations.

WTF: Unfortunately, exception management don't work with ABCs in Python 3.
(See issue #\ 12029_).

A mechanism compatible with all versions for this pattern could be found in
this module.

.. _12029: http://bugs.python.org/issue12029

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from xoutil.eight.meta import metaclass
from xoutil.eight.abc import ABC, ABCMeta


class Handler(ABC):
    '''Base class for all Xoutil Handlers.

    Handlers are concepts that require an API definition in low level layers
    (protocols), and specific implementations within concrete applications.

    The following convention will be used:

    - API Interface: Any of the `Handler` sub-classes that are declared inner
      foundation and common layers (for example, `Xoutil`).

    - API Tools: All non-empty methods and module -global- functions related
      to an API Interface.

    - API Kind: Any interface defining a core concept.  Normally are direct
      `Handler`:class: sub-classes and always have sub-classes in a concrete
      execution context.

    - Driver: `Handler` sub-classes that don't have further sub-classes and
      are unique in its kind within an execution context.

    - Fixing: Localization of the implementation for the driver given the
      handler kind.  The class-method `locate_driver_class`:meth: will obtain
      the proper driver class in the current execution context.

      Applications implementing drivers must use a mechanism of "Convention
      over Configuration" (CoC) to register their classes.  The simplest one
      is to guarantee that all modules containing needed drivers are loaded
      starting each execution context.

    - A driver could define a mechanism to validate if current execution
      context is applicable to its function or not.  See
      `is_applicable_for_context`:meth:.  This will support the fixing
      process.

      If more than one driver class is applicable for a handler kind within a
      context (even when someone -myself included- could say: "WTF"), an
      additional mechanism could be applied using the
      `get_importance_for_context`:meth: method.

    - Decorator `abstractmethod` use is an obligation indicator for methods
      must be implemented in the concrete layers.

    - Drivers could implement a set of "distinguishing features of its nature"
      (traits) that must be documented by redefining the
      `list_of_traits`:meth: method.  Each trait item will be a dictionary
      compliant value using the key names 'name' and 'type' as reserved and
      mandatory; and 'desc', and 'tags' as reserved and optional.

    '''
    def __str__(self):
        '''The "informal" string representation of a handler.'''
        return self._get_typed_desc()

    def __repr__(self):
        '''The "official" string representation of a handler.'''
        return '<{}>'.format(str(self))

    @classmethod
    def locate_driver_class(cls):
        '''Find a driver class for the given handler kind (cls).

        :param cls: Class representing a Handler Kind.

        This method must not be called in a driver.

        '''
        if cls is Handler:
            aux = list(get_leaf_classes(cls) - {cls})
            ok = is_driver_applicable_for_context
            drivers = [drv for drv in aux if ok(drv)]
            count = len(drivers)
            if count == 1:
                return drivers[0]
            elif count > 1:
                res, rank = None, None
                count = 0
                get_rank = get_driver_importance_for_context
                for drv in drivers:
                    new_rank = get_rank(drv)
                    if not res or rank < new_rank:
                        res, rank = drv, new_rank
                        count = 1
                    elif rank == new_rank:
                        count += 1
                if count == 1:
                    return res
                else:
                    assert count > 1
                    msg = 'Too many "{}" handler drivers obtained ({}).'
                    raise RuntimeError(msg.format(cls.__name__, count))
            else:
                msg = ('No "{}" handler driver found. Maybe you need to load '
                       'some missing modules.')
                raise RuntimeError(msg.format(cls.__name__))
        else:
            raise NotImplementedError('Method `locate_driver_class` is not '
                                      'implemented at `Handler` level.')

    @classmethod
    def is_applicable_for_context(cls):
        '''True if a driver is valid in current execution context.

        Must be redefined in drivers that could result invalids in some
        contexts.

        '''
        return True

    @classmethod
    def get_importance_for_context(cls):
        '''Rank of a driver.

        Must be redefined in drivers wishing to increase -or decrease- the
        level of importance.  The standard value is the integer "0".

        '''
        return 0

    @classmethod
    def list_of_traits(cls):
        '''Distinguishing features of specific handler driver nature.

        This method returns an iterator of dictionaries.  There are some
        reserved keys:

        - name: The feature name.

        - type: The kind or category of the feature.

        - desc: The feature description or documentation.

        - tags: Classifiers or descriptors for the feature.

        "name" and "type" are required.

        This is pure literate programming; if a feature is of type 'method'
        (or 'verb', a synonym) always you can call directly Python object
        methods representing these traits.

        '''
        return ()

    def _get_typed_desc(self):
        return '{}: {}'.format(type(self).__name__, self._get_untyped_desc())

    def _get_untyped_desc(self):
        from xoutil.object import multi_getter
        name, domain = multi_getter(self, 'name', 'domain')
        if name:
            return '{} ({})'.format(name, domain) if domain else name
        elif domain:
            return domain
        else:
            return hex(id(self))


class Error(Exception, ABC):
    '''Base class for all Xoutil API Exceptions.

    Allow to register concrete driver error classes in generic Xoutil
    exceptions.

    This class is an ABC in order to allow drivers to map concrete error
    classes using `adopt`:meth: method.

    For example::

      # --- In a general layer module (myapi) ---

      >>> from xoutil import api
      >>> @api.error
      ... class ResourceNotFoundError(Exception):
      ...    pass

      # --- In a driver implementation ---

      >>> import couchdb
      >>> myapi.ResourceNotFoundError.adopt(couchdb.http.ResourceNotFound)

      # --- In any code managing this exception (drivers) ---

      try:
          ...
      except api.error.ResourceNotFoundError:
          # catch registered exceptions (e.g. couchdb.http.ResourceNotFound)
          pass

    '''
    pass


def is_error_class(value):
    return isinstance(value, type) and issubclass(value, BaseException)


def _is_abc_nice_with_errors():
    '''See if ABCs works nice or not in this Python version.'''
    @Error.adopt
    class TestError(Exception):
        pass
    try:
        raise TestError('Any msg.')
    except Error:
        return True
    except Exception:
        return False

_ABC_NICE_WITH_ERRORS = _is_abc_nice_with_errors()


class _bag_assign(object):
    '''An execution context to block direct `ErrorBag` error assignments.'''
    @classmethod
    def enter(cls):
        '''Enter the context.

        Use as ``with _bag_assign.enter()``: ...

        '''
        from xoutil.context import context
        return context(cls)

    @classmethod
    def check(cls):
        '''Check if inner the context.'''
        from xoutil.context import context
        return bool(context[cls])


class ErrorBagMeta(ABCMeta):
    '''Meta-class for a bag of errors that need adaption.'''
    def __new__(cls, name, bases, attrs):
        if name == 'ErrorBag' and attrs.get('__module__') == __name__:
            _super = super(ErrorBagMeta, cls).__new__
            with _bag_assign.enter():
                return _super(cls, name, bases, attrs)
        else:
            raise RuntimeError('Only one instance of errors bag is allowed.')

    def __setattr__(self, name, value):
        is_err = is_error_class(value)
        if _bag_assign.check() or not (is_err or isinstance(value, self)):
            super(ErrorBagMeta, self).__setattr__(name, value)
        else:
            if is_err:
                kind = 'layer error'
                aux = value
            else:
                kind = 'internal error descriptor'
                aux = value.wrapped
            msg = 'API {} "{}" can\'t be directly assigned.'
            raise ValueError(msg.format(kind, aux.__name__))


class ErrorBag(metaclass(ErrorBagMeta)):
    '''Singleton for API error definitions (the bag).

    An API Error is something declared at a generic level and is mapped to
    concrete errors in specific implementations.  See `Error`:class: class for
    more information.

    Don't use this class directly with its name, use instead the declared
    alias "error".

    To adopt a generic error base, just use this class as a decorator; for
    example::

      >>> from xoutil import api
      >>> @api.error
      ... class ResourceNotFoundError(Exception):
      ...     pass

    '''
    def __new__(cls, wrapped):
        assert cls is ErrorBag
        if is_error_class(wrapped):
            if _ABC_NICE_WITH_ERRORS:
                self = wrapped
            else:
                self = super(ErrorBag, cls).__new__(cls)
                self.wrapped = wrapped
            name = wrapped.__name__
            if not hasattr(cls, name):
                with _bag_assign.enter():
                    # to avoid direct assigning block
                    setattr(cls, name, self)
                return wrapped
            else:
                raise RuntimeError('Error "{}" already adopted.'.format(name))
        else:
            from xoutil.names import simple_name
            msg = 'Parameter `wrapped` must be an exception class, not "{}".'
            raise TypeError(msg.format(simple_name(wrapped)))

    def __init__(self, wrapped):
        pass

    def __get__(self, obj, owner):
        import sys
        if obj is None:
            assert owner is ErrorBag
            cls = sys.exc_info()[0]
            if cls is not None and issubclass(cls, self.wrapped):
                return cls
            else:
                return self.wrapped


error = ErrorBag


def _abc_registered(cls):
    '''Internal class to get all ABC registered classes in a Python set.'''
    from abc import ABCMeta
    if isinstance(cls, ABCMeta):
        return set(cls._abc_registry)
    else:
        return set()


def get_leaf_classes(cls):
    '''List all branch sub-classes"

    A branch class don't have further sub-classes (either declared as Python
    inheritance or ABC registered).

    '''
    inner = set(type.__subclasses__(cls)) | _abc_registered(cls)
    if inner:
        res = set()
        for i in inner:
            if i not in res:
                for j in get_leaf_classes(i):
                    res.add(j)
        return res
    else:
        return {cls}


def is_driver_applicable_for_context(driver):
    '''Utility function to call `is_applicable_for_context` in drivers.

    If the `driver` was adopted using ABC, it's probable that miss the method
    `is_applicable_for_context`; in that case this function returns True.

    '''
    try:
        return driver.is_applicable_for_context()
    except AttributeError:
        return True


def get_driver_importance_for_context(driver):
    '''Utility function to call `get_importance_for_context` in drivers.

    If the `driver` was adopted using ABC, it's probable that miss the method
    `get_importance_for_context`; in that case this function returns 0.

    '''
    try:
        return driver.get_importance_for_context()
    except AttributeError:
        return 0
