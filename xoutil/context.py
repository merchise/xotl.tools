#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''A context manager for execution context flags.'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.tasking import local
from xoutil.future.collections import StackedDict, Mapping

__all__ = ('Context', 'context', 'NullContext')


class LocalData(local):
    '''Thread-local data for contexts.'''
    def __init__(self):
        super().__init__()
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


class Context(StackedDict, metaclass=MetaContext):
    '''An execution context manager with parameters (or flags).

    Use as::

        >>> SOME_CONTEXT = object()
        >>> from xoutil.context import context
        >>> with context(SOME_CONTEXT):
        ...     if context[SOME_CONTEXT]:
        ...         print('In context SOME_CONTEXT')
        In context SOME_CONTEXT

    Note the difference creating the context and checking it: for entering a
    context you should use ``context(name)`` for testing whether some piece of
    code is being executed inside a context you should use ``context[name]``;
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
    values. Each new written value is stored in current level without
    affecting upper levels.

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
    __slots__ = ('name', 'count', )

    def __new__(cls, name, **data):
        self = cls[name]
        if not self:     # if self is _null_context:
            self = super().__new__(cls)
            super(Context, self).__init__()
            self.name = name
            self.count = 0
            # TODO: Redefine all event management
        return self(**data)

    @classmethod
    def from_dicts(cls, ctx, overrides=None, defaults=None):
        '''Creates a context introducing both defaults and overrides.

        This combines both the standard constructor and `from_defaults`:meth:.

        If the same key appears in both `overrides` and `defaults`, ignore the
        default.

        '''
        if not overrides:
            overrides = {}
        if not defaults:
            defaults = {}
        current = cls[ctx]
        current_attrs = dict(current) if current else {}
        attrs = dict(defaults, **current_attrs)
        attrs.update(overrides)
        return cls(ctx, **attrs)

    @classmethod
    def from_defaults(cls, ctx, **defaults):
        '''Creates context `ctx` introducing only new keys given in `defaults`.

        The normal behavior when you enter a new level in the context is to
        override the values with the new one.

        Example:

           >>> with context.from_defaults('A', a=1):
           ...    with context.from_defaults('A', a=2, b=1) as c:
           ...        assert c['a'] == 1

        '''
        return cls.from_dicts(ctx, defaults=defaults)

    def __init__(self, *args, **kwargs):
        '''Must be defined empty for `__new__` parameters compatibility.

        Using generic parameters definition allow any redefinition of this
        class can use this `__init__`.

        '''

    def __call__(self, **data):
        '''Allow re-enter in a new level to an already assigned context.'''
        self.push_level(**data)
        return self

    def __nonzero__(self):
        return bool(self.count)
    __bool__ = __nonzero__

    def __enter__(self):
        if self.count == 0:
            _data.contexts[self.name] = self
        if self.count + 1 == self.level:
            self.count += 1
            return self
        else:
            msg = 'Entering the same context level twice! -- c(%s, %d, %d)'
            raise RuntimeError(msg % (self.name, self.count, self.level))

    def __exit__(self, exc_type, exc_value, traceback):
        self.count -= 1
        if self.count == 0:
            del _data.contexts[self.name]
        self.pop_level()
        return False


# A simple alias for Context
context = Context


class NullContext(Mapping):
    '''Singleton context to be used (returned) as default when no one is
    defined.

    '''

    __slots__ = ()

    instance = None
    name = ''

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __len__(self):
        return 0

    def __iter__(self):
        return iter(())

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

    @property
    def level(self):
        return 0


_null_context = NullContext()


from collections import Mapping

Mapping.register(NullContext)

del Mapping
