# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.context
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
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
                        unicode_literals as _py3_unicode)

from threading import local
from xoutil.decorator.compat import metaclass

class LocalData(local):
    def __init__(self):
        super(LocalData, self).__init__()
        self.contexts = {}

_data = LocalData()


class MetaContext(type):
    def __getitem__(self, name):
        return _data.contexts.get(name, _null_context)

    def __contains__(self, name):
        '''
        Basic support for the 'A in context' idiom::

            >>> from xoutil.context import context
            >>> with context('A'):
            ...    if 'A' in context:
            ...        print('A')
            A

        '''
        return bool(self[name])


@metaclass(MetaContext)
class Context(object):
    '''A context manager for execution context flags.

    Use as::

        >>> from xoutil.context import context
        >>> with context('somename'):
        ...     if context['somename']:
        ...         print('In context somename')
        In context somename

    Note the difference creating the context and checking it: for entering a
    context you should use `context(name)` for testing whether some piece of
    code is being executed inside a context you should use `context[name]`;
    you may also use the syntax `name in context`.

    If you pass keyword argument, those will be accesible by the :attr:`data`
    of the context object.

    '''
    def __new__(cls, name, **data):
        res = cls[name]
        if res is _null_context:
            res = super(Context, cls).__new__(cls)
            res.name = name
            res._data = [data]
            res.count = 0
            res._events = []
        else:
            res._data.append(data)
        return res

    def __nonzero__(self):
        return self.count

    def __enter__(self):
        if self.count == 0:
            _data.contexts[self.name] = self
        self.count += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.count -= 1
        ctx = _data.contexts[self.name]
        ctx._data.pop(-1)
        if self.count == 0:
            for event in self.events:
                event(self)
            del _data.contexts[self.name]
        return False

    @property
    def events(self):
        return self._events

    @events.setter
    def events(self, value):
        self._events = list(value)

    @property
    def data(self):
        # TODO: Make this a proper collection
        class stackeddict(object):
            def __init__(self, dicts):
                self._dicts = dicts
            def get(self, name, default=None):
                from xoutil.objects import get_first_of
                unset = object()
                res = get_first_of(list(reversed(self._dicts)),
                                   name, default=unset)
                if res is not unset:
                    return res
                else:
                    return default
            def __getitem__(self, name):
                unset = object()
                res = self.get(name)
                if res is not unset:
                    return res
                else:
                    raise KeyError(name)
            def __setitem__(self, name, value):
                self._dicts[-1][name] = value
            def __iter__(self):
                return iter(self._dicts[-1])
            def __getattr__(self, name):
                return self[name]
            def __setattr__(self, name, value):
                if not name.startswith('_'):
                    self[name] = value
                else:
                    super(stackeddict, self).__setattr__(name, value)
        return stackeddict(self._data)

    def setdefault(self, key, value):
        return self.data.setdefault(key, value)


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

    @property
    def data(self):
        return {}

    def __nonzero__(self):
        return False
    __bool__ = __nonzero__

    def __enter__(self):
        from xoutil.types import Unset
        return Unset

    def __exit__(self, exc_type, exc_value, traceback):
        return False


_null_context = NullContext()


class SimpleClose(object):
    '''A very simple close manager that just call the argument function exiting
    the manager.

    '''
    def __init__(self, close_funct, *args, **kwargs):
        self.close_funct = close_funct
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_funct(*self.args, **self.kwargs)
        return False
