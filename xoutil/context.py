# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.context
# ---------------------------------------------------------------------
# Copyright (c) 2013-2015 Merchise Autrement and Contributors
# Copyright (c) 2011, 2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Mar 9, 2011
#


'''
A context manager for execution context flags.

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


from xoutil._local import local as _local

from xoutil.objects import metaclass
from xoutil.collections import StackedDict

from xoutil.names import strlist as strs
__all__ = strs('Context', 'context', 'NulContext')
del strs


class LocalData(_local):
    def __init__(self):
        super(LocalData, self).__init__()
        self.contexts = {}

_data = LocalData()


class MetaContext(type(StackedDict)):
    def __len__(self):
        return len(_data.contexts)

    def __iter__(self):
        return iter(_data.contexts)

    def __getitem__(self, name):
        return _data.contexts.get(name, _null_context)

    def __contains__(self, name):
        '''Basic support for the 'A in context' idiom.'''
        return bool(self[name])


class Context(metaclass(MetaContext), StackedDict):
    '''A context manager for execution context flags.

    Use as::

        >>> SOME_CONTEXT = object()
        >>> from xoutil.context import context
        >>> with context(SOME_CONTEXT):
        ...     if context[SOME_CONTEXT]:
        ...         print('In context SOME_CONTEXT')
        In context SOME_CONTEXT

    Note the difference creating the context and checking it: for entering a
    context you should use `context(name)` for testing whether some piece of
    code is being executed inside a context you should use `context[name]`;
    you may also use the syntax `name in context`.

    When an existing context is re-enter, the former one is reused.
    Nevertheless, the data stored in each context is local to each level.

    For example::

        >>> with context('A', b=1) as a1:
        ...   with context('A', b=2) as a2:
        ...       print(a1 is a2)
        ...       print(a2['b'])
        ...   print(a1['b'])
        True
        2
        1

    For data access, a mapping interface is provided for all contexts. If a
    data slot is deleted at some level, upper level is used to read
    values. Each new written value is stored in current level without affecting
    upper levels.

    For example::

        >>> with context('A', b=1) as a1:
        ...   with context('A', b=2) as a2:
        ...       del a2['b']
        ...       print(a2['b'])
        1

    It is an error to *reuse* a context directly like in::

        >>> with context('A', b=1) as a1:   # doctest: +ELLIPSIS
        ...   with a1:
        ...       pass
        Traceback (most recent call last):
        ...
        RuntimeError: Entering the same context level twice! ...

    '''
    __slots__ = ('name', 'count', '_events')

    def __new__(cls, name, **data):
        self = cls[name]
        if not self:     # if self is _null_context:
            self = super(Context, cls).__new__(cls)
            super(Context, self).__init__()
            self.name = name
            self.count = 0
            # TODO: Redefine all event management
            self._events = []
        self.push(**data)
        return self

    def __init__(self, name, **data):
        pass

    def __nonzero__(self):
        return bool(self.count)
    __bool__ = __nonzero__

    def __enter__(self):
        if self.count == 0:
            _data.contexts[self.name] = self
        self.count += 1
        if self.count == self.level:
            return self
        else:
            msg = 'Entering the same context level twice! -- c(%s, %d, %d)'
            raise RuntimeError(msg % (self.name, self.count, self.level))

    def __exit__(self, exc_type, exc_value, traceback):
        self.count -= 1
        if self.count == 0:
            for event in self.events:
                event(self)
            del _data.contexts[self.name]
        self.pop()
        return False

    @property
    def events(self):
        return self._events

    @events.setter
    def events(self, value):
        self._events = list(value)


# A simple alias for Context
context = Context


class NullContext(object):
    '''Singleton context to be used (returned) as default when no one is
    defined.

    '''

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(NullContext, cls).__new__(cls)
        return cls.instance

    def __len__(self):
        return 0

    def __iter__(self):
        return ()

    def __getitem__(self, key):
        raise KeyError(key)

    def __nonzero__(self):
        return False
    __bool__ = __nonzero__

    def __enter__(self):
        return _null_context

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def get(self, name, default=None):
        return default


_null_context = NullContext()


from collections import Mapping

Mapping.register(NullContext)

del Mapping
