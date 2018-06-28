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
                        absolute_import as _py3_abs_imports)

from threading import *    # noqa
from threading import Event, Thread, RLock, Timer
from xoutil.deprecation import deprecate_linked
deprecate_linked()
del deprecate_linked


def async_call(func, args=None, kwargs=None, callback=None, onerror=None):
    '''Executes a function asynchronously.

    The function receives the given positional and keyword arguments

    If `callback` is provided, it is called with a single positional argument:
    the result of calling `func(*args, **kwargs)`.

    If the called function ends with an exception and `onerror` is provided, it
    is called with the exception object.

    :returns: An event object that gets signalled when the function ends its
              execution whether normally or with an error.

    :rtype: `Event`:class:

    '''
    event = Event()
    event.clear()
    if not args:
        args = ()
    if not kwargs:
        kwargs = {}

    def async_():
        try:
            result = func(*args, **kwargs)
            if callback:
                callback(result)
        except Exception as error:
            if onerror:
                onerror(error)
        finally:
            event.set()

    thread = Thread(target=async_)
    thread.setDaemon(True)  # XXX: Why?
    thread.start()
    return event


class _SyncronizedCaller(object):
    '''Protected to be used in `sync_call`:func:'''
    def __init__(self, pooling=0.005):
        self.lock = RLock()
        self._not_bailed = True
        self.pooling = pooling

    def __call__(self, funcs, callback, timeout=None):
        def _syncronized_callback(result):
            with self.lock:
                if self._not_bailed:
                    callback(result)

        events, threads = [], []
        for which in funcs:
            event, thread = async_call(which, callback=_syncronized_callback)
            events.append(event)
            threads.append(thread)
        if timeout:
            def set_all_events():
                with self.lock:
                    self._not_bailed = False
                for e in events:
                    e.set()
            timer = Timer(timeout, set_all_events)
            timer.start()
        while events:
            terminated = []
            for event in events:
                flag = event.wait(self.pooling)
                if flag:
                    terminated.append(event)
            for e in terminated:
                events.remove(e)
        if timeout:
            timer.cancel()


def sync_call(funcs, callback, timeout=None):
    '''Calls several functions, each one in it's own thread.

    Waits for all to end.

    Each time a function ends the `callback` is called (wrapped in a lock to
    avoid race conditions) with the result of the as a single positional
    argument.

    If `timeout` is not None it sould be a float number indicading the seconds
    to wait before aborting. Functions that terminated before the timeout will
    have called `callback`, but those that are still working will be ignored.

    .. todo:: Abort the execution of a thread.

    :param funcs: A sequences of callables that receive no arguments.

    '''
    sync_caller = _SyncronizedCaller()
    sync_caller(funcs, callback, timeout)


from threading import __all__    # noqa
__all__ = list(__all__) + ['async_call', 'sync_call']
