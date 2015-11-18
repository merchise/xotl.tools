#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.logical
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2015-02-23

'''Fixed special logical values like Unset, Ignored, Required, etc...

All values only could be `True` or `False` but are intended in places where
`None` is expected to be a valid value or for special Boolean formats.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

# TODO: See `sqlalchemy.util.langhelpers.symbol` class
from abc import ABCMeta
from .eight.meta import metaclass

from xoutil.tasking import local


class _local_data(local):
    def __init__(self):
        # from weakref import WeakValueDictionary as maptype
        maptype = dict    # TODO: weak refs not working with slots in Python3
        super(_local_data, self).__init__()
        self.instances = maptype()

_ldata = _local_data()

del local


class MetaLogical(ABCMeta):
    '''Metaclass for logical types.'''

    def __init__(self, name, bases, attrs):
        if bases == (int,):
            super(MetaLogical, self).__init__(name, bases, attrs)
            self.register(bool)
        else:
            msg = 'only `int` sub-classes are allowed, "{}" used'
            raise TypeError(msg.format(tuple(b.__name__ for b in bases)))

    def _get_instance(self, name, value):
        '''Get or create a new logical instance.

        :param name: String representing the internal name.  Logical instances
               are unique (singletons) in the context of this argument.  ``#``
               and spaces are invalid characters to allow comments.

        :param value: Any value compatible with Python `bool` (Always is
               converted to this type before using it).  Default is `False`.

        This method is only intended to be called from `__new__` special
        method implementations.

        '''
        from .eight import intern as unique
        name = unique(name)
        if name:
            value = bool(value)
            res = _ldata.instances.get(name)
            if res is None:    # Create the new instance
                res = super(self, self).__new__(self, value)
                _ldata.instances[name] = res
            elif res != value:    # Check existing instance
                msg = 'Incorrect value for existing instance: %s '
                raise ValueError(msg % name)
            return res
        else:
            raise ValueError('Name must be a valid non empty string!')

    def get_name(self, value):
        '''Returns name of a given logical instance (:param value:).

        Standard Python Boolean values are valid too.

        '''
        try:
            d = _ldata.instances
            items = ((name, d[name]) for name in d)
            return next(name for name, obj in items if obj is value)
        except StopIteration:
            return repr(bool(value))

    def parse(self, value):
        '''Returns instance (or None if not found) from a string.

        Standard Python Boolean values are parsed too.

        '''
        if '#' in value:    # Remove comment
            value = value.split('#')[0].strip()
        key = next((key for key in _ldata.instances if key == value), None)
        if key is not None:
            return _ldata.instances[key]
        else:
            try:    # Standard Python Boolean values
                res = eval(value)
                if not (res is True or res is False):
                    res = None
            except:
                res = None
            return res


class Logical(metaclass(MetaLogical), int):
    '''Instances are custom logical values (`True` or `False`).

    See :meth:`~MetaLogical._get_instance` method for information on
    constructor arguments.

    For example::

      >>> true = Logical('true', True)
      >>> false = Logical('false')
      >>> none = Logical('false')
      >>> unset = Logical('unset')

      >>> class X(object):
      ...      attr = None

      >>> getattr(X(), 'attr') is not None
      False

      >>> getattr(X(), 'attr', false) is not false
      True

      >>> none is false
      True

      >>> false == False
      True

      >>> false == unset
      True

      >>> false is unset
      False

      >>> true == True
      True

    '''

    __slots__ = ()

    def __new__(cls, name, value=False):
        '''Constructor of a new instance.'''
        return cls._get_instance(name, value)

    def __repr__(self):
        return type(self).get_name(self)

    __str__ = __repr__


del ABCMeta, metaclass
