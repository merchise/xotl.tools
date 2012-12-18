# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.context
#----------------------------------------------------------------------
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

Use as:

    >>> from xoutil.context import context
    >>> with context('somename'):
    ...     if context['somename']:
    ...         print('In context somename')
    In context somename

Note the difference creating the context and checking it.

If module `zope.interface` is installed, then you may ask for
interfaces in context::

   >>> from zope.interface import Interface, implementer
   >>> class IFoo(Interface):
   ...    pass

   >>> class IBar(IFoo):
   ...    pass

   >>> @implementer(IBar)
   ... class Bar(object):
   ...    pass

   >>> bar = Bar()
   >>> ham = Bar()

   >>> with context(bar):
   ...    if context[IFoo]:
   ...        print('IFoo')
   IFoo

Notice that the context object is *not* the name::

    >>> with context(bar) as ctx:
    ...    if bar is not ctx:
    ...        print('bar not ctx')
    bar not ctx

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

from threading import local

from xoutil.collections import OrderedDict
from xoutil.compat import iteritems_

try:
    from zope.interface import Interface
except ImportError:
    Interface = None


class LocalData(local):
    def __init__(self):
        super(LocalData, self).__init__()
        self.contexts = OrderedDict()

_data = LocalData()


class MetaContext(type):
    def __getitem__(self, name):
        result = _data.contexts.get(name, None)
        if result:
            return result
        elif Interface and not result and type(name) is type(Interface):
            candidates = list((len(type(which).mro()), context)
                               for which, context in iteritems_(_data.contexts)
                               if name.providedBy(which))
            if candidates:
                # Returns the most specific and last
                candidates.sort(key=lambda (depth, cls): depth, reverse=True)
                return candidates[0][-1]
            else:
                return _null_context
        else:
            return _null_context

    def __contains__(self, name):
        '''
        Basic cupport for the 'A in context' idiom::

            >>> from xoutil.context import context
            >>> with context('A'):
            ...    if 'A' in context:
            ...        print('A')
            A
        '''
        return bool(self[name])


class Context(object):
    '''
    A context manager for execution context flags.

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
    '''
    __metaclass__ = MetaContext

    def __new__(cls, name, **data):
        res = cls[name]
        if res is _null_context:
            res = super(Context, cls).__new__(cls)
            res.name = name
            res.data = data
            res.count = 0
            res._events = []
        elif data:
            res.data.update(data)
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
        self._events = list(set(value))

    def setdefault(self, key, value):
        return self.data.setdefault(key, value)


# A simple alias for Context
context = Context


class NullContext(object):
    '''
    Singleton context to be used (returned) as default when no one is defined.
    '''

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(NullContext, cls).__new__(cls)
        return cls.instance

    def __nonzero__(self):
        return False

    def __enter__(self):
        from xoutil.types import Unset
        return Unset

    def __exit__(self, exc_type, exc_value, traceback):
        return False


_null_context = NullContext()


class SimpleClose(object):
    '''
    A very simple close manager that just call the argument function exiting
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
