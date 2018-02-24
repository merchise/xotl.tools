#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


# This module is a modified copy of gevent.local.  We simply modify it to
# allow absence of greenlets, and fallback to thread isolation in this case.
#
# This decouples xoutil.context from gevent and allows to use the greenlets if
# available.

# WARNING: We removed the greenlet protection gevent.local does while
# initializing a subclass of `local`.  Instead we simply provide protection at
# the thread level, so sub-classes of `local` MUST NOT switch greenlets.
from threading import RLock


# since each thread has its own greenlet we can just use those as identifiers
# for the context.  If greenlets are not available we fall back to the
# current thread ident depending on where it is.
try:
    from greenlet import getcurrent
except ImportError:
    from threading import current_thread as getcurrent


from weakref import WeakKeyDictionary
from copy import copy


import sys
PYPY = hasattr(sys, 'pypy_version_info')

__all__ = ["local"]


class _localbase(object):
    __slots__ = '_local__args', '_local__lock', '_local__dicts'

    def __new__(cls, *args, **kw):
        self = object.__new__(cls)
        object.__setattr__(self, '_local__args', (args, kw))
        object.__setattr__(self, '_local__lock', RLock())
        dicts = WeakKeyDictionary()
        object.__setattr__(self, '_local__dicts', dicts)

        if args or kw:
            clsi, obji = cls.__init__, object.__init__
            if (PYPY and clsi == obji) or (not PYPY and clsi is obji):
                raise TypeError("Initialization arguments are not supported")

        # We need to create the greenlet dict in anticipation of
        # __init__ being called, to make sure we don't call it again ourselves.
        dict = object.__getattribute__(self, '__dict__')
        dicts[getcurrent()] = dict
        return self


def _init_locals(self):
    d = {}
    dicts = object.__getattribute__(self, '_local__dicts')
    dicts[getcurrent()] = d
    object.__setattr__(self, '__dict__', d)

    # we have a new instance dict, so call out __init__ if we have one
    cls = type(self)
    if cls.__init__ is not object.__init__:
        args, kw = object.__getattribute__(self, '_local__args')
        cls.__init__(self, *args, **kw)


class local(_localbase):
    '''Greenlet-local data.'''
    def __getattribute__(self, name):
        d = object.__getattribute__(self, '_local__dicts').get(getcurrent())
        if d is None:
            # it's OK to acquire the lock here and not earlier, because the
            # above code won't switch out however, subclassed __init__ might
            # switch, so we do need to acquire the lock here
            lock = object.__getattribute__(self, '_local__lock')
            lock.acquire()
            try:
                _init_locals(self)
                return object.__getattribute__(self, name)
            finally:
                lock.release()
        else:
            object.__setattr__(self, '__dict__', d)
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name == '__dict__':
            clsname = self.__class__.__name__
            raise AttributeError(
                "%r object attribute '__dict__' is read-only" % clsname
            )
        d = object.__getattribute__(self, '_local__dicts').get(getcurrent())
        if d is None:
            lock = object.__getattribute__(self, '_local__lock')
            lock.acquire()
            try:
                _init_locals(self)
                return object.__setattr__(self, name, value)
            finally:
                lock.release()
        else:
            object.__setattr__(self, '__dict__', d)
            return object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name == '__dict__':
            clsname = self.__class__.__name__
            raise AttributeError(
                "%r object attribute '__dict__' is read-only" % clsname
            )
        d = object.__getattribute__(self, '_local__dicts').get(getcurrent())
        if d is None:
            lock = object.__getattribute__(self, '_local__lock')
            lock.acquire()
            try:
                _init_locals(self)
                return object.__delattr__(self, name)
            finally:
                lock.release()
        else:
            object.__setattr__(self, '__dict__', d)
            return object.__delattr__(self, name)

    def __copy__(self):
        currentId = getcurrent()
        d = object.__getattribute__(self, '_local__dicts').get(currentId)
        duplicate = copy(d)

        cls = type(self)
        if cls.__init__ is not object.__init__:
            args, kw = object.__getattribute__(self, '_local__args')
            instance = cls(*args, **kw)
        else:
            instance = cls()

        object.__setattr__(instance, '_local__dicts', {
            currentId: duplicate
        })

        return instance
