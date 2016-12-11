#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.api
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-10-19

'''Support the abstraction layer intended for API definitions.

There are architectures that need to split solutions in interfaces and general
tools in low-level layers (foundation and common systems) and to adapt them in
concrete layers (industry and organization-specific).

Concrete implementations could use the same API interfaces and common tools
but disparate technologies and frameworks.

There are two base classes that allow such definitions:

- `Handler`:class:`\ : A base class -or ABC register- that allow to define
  interfaces and tools (in foundation and common layers) representing specific
  driver implementations.

- `BaseError`:class:`\ : Base to sub-class generic errors that could adopt
  different shapes in specific handler driver implementations.

Mapping mechanisms allow to fix the corresponding specific class for a general
concept of a kind defined in the API layer.

In Python there is a very nice mechanism for this kind of mapping: "Abstract
Base Classes (ABCs)".  Unfortunately it doesn't work for exceptions in some
Python versions.  Because of that, this mechanism is extended for API errors
in  internal module `xoutil.api._errors`:mod:.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from xoutil.eight.abc import ABC
from ._errors import BaseError, error    # noqa


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
