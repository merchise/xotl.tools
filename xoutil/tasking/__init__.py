#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.tasking
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-10-25

'''Task, multitasking, and concurrent programming tools.

.. warning:: Experimental.  API is not settled.

.. versionadded:: 1.8.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import sys
from xoutil.decorator.meta import decorator


# TODO: Must be implemented using `xoutil.api` mechanisms for correct driver
# determination, in this case "thread-local data".
if 'greenlet' in sys.modules:
    from ._greenlet_local import local    # noqa
else:
    try:
        from threading import local    # noqa
    except ImportError:
        from dummy_threading import local    # noqa

del sys


class AutoLocal(local):
    '''Initialize thread-safe local data in one shoot.

    Typical use is::

        >>> from xoutil.tasking import AutoLocal
        >>> context = AutoLocal(cause=None, traceback=None)

    When at least one attribute is given, ``del AutoLocal`` it's executed
    automatically avoiding this common statement at the end of your module.

    '''
    def __init__(self, **attrs):
        import sys
        super(AutoLocal, self).__init__()
        for attr in attrs:
            setattr(self, attr, attrs[attr])
        if attrs:
            g = sys._getframe(1).f_globals
            tname = type(self).__name__
            if tname in g:
                del g[tname]


#: The minimal time (in seconds) to wait between retries.
#:
#: .. versionadded:: 1.8.2
MIN_WAIT_INTERVAL = 20 / 1000  # 20 ms

#: The default time (in seconds) to wait between retries.
#:
#: .. versionadded:: 1.8.2
DEFAULT_WAIT_INTERVAL = 50 / 1000  # 50 ms


class StandardWait(object):
    '''A standard constant wait algorithm.

    Instances are callables that comply with the need of `dispatcher`:func:\
    's `wait` argument.  This callable always return the same `wait` value.

    We never wait less than `MIN_WAIT_INTERVAL`:data:.

    .. versionadded:: 1.8.2

    '''
    def __init__(self, wait=DEFAULT_WAIT_INTERVAL):
        import numbers
        if not isinstance(wait, numbers.Real):
            raise TypeError("'wait' must a number.")
        self.wait = max(MIN_WAIT_INTERVAL, wait)

    def __call__(self, prev=None):
        return self.wait


class BackoffWait(object):
    '''A wait algorithm with an exponential backoff.

    Instances are callables that comply with the need of `dispatcher`:func:\
    's `wait` argument.

    At each call the wait is increased by doubling `backoff` (given in
    milliseconds).

    We never wait less than `MIN_WAIT_INTERVAL`:data:.

    .. versionadded:: 1.8.2

    '''
    def __init__(self, wait=DEFAULT_WAIT_INTERVAL, backoff=5):
        self.wait = max(MIN_WAIT_INTERVAL, wait)
        self.backoff = min(max(0.1, backoff), 1)

    def __call__(self, prev=None):
        res = self.wait + (self.backoff / 1000)
        self.backoff = self.backoff * 2
        return res


def dispatch(fn, *args, **kwargs):
    '''Run `fn` with args and kwargs in an auto-retrying loop.

    See `dispatcher`:class:.  This is just::

       >>> dispatcher(max_tries=max_tries, max_time=max_time, wait=wait,
       ...            retry_only=retry_only)(fn, *args, **kwargs)

    .. versionadded:: 1.8.2

    '''
    from xoutil.params import ParamManager, check_count
    check_count(args, 0, 2)
    pm = ParamManager(args, kwargs)
    fnargs = pm(0, 'args', default=())
    fnkwargs = pm(1, 'kwargs', default={})
    max_tries = pm('max_tries', default=None)
    max_time = pm('max_time', default=None)
    wait = pm('wait', default=DEFAULT_WAIT_INTERVAL)
    retry_only = pm('retry_only', default=None)
    return dispatcher(max_tries=max_tries, max_time=max_time, wait=wait,
                      retry_only=retry_only)(fn, *fnargs, **fnkwargs)


def dispatcher(max_tries=None, max_time=None,
               wait=DEFAULT_WAIT_INTERVAL, retry_only=None):
    '''An auto-retrying dispatcher.

    Return a callable that take another callable (`func`) and its arguments
    and runs it in an auto-retrying loop.

    If `func` raises any exception that is in `retry_only`, and it has being
    tried less than `max_tries` and the time spent executing the function
    (waiting included) has not reached `max_time`, the function will be
    retried.

    `wait` can be a callable or a number.  If `wait` is callable, it must take
    a single argument with the previous waiting we did (`None`:data: for the
    first retry) and return the number of seconds to wait before retrying.

    If `wait` is a number, we convert it to a callable with
    `StandardWait(wait) <StandardWait>`:class:.

    .. seealso:: `BackoffWait`:class:

    If `retry_only` is None, all exceptions (that inherits from Exception)
    will be retried.  Otherwise, only the exceptions in `retry_only` will be
    retried.

    Waiting is done with `time.sleep`:func:.  Time tracking is done with
    `time.monotonic`:func:.

    .. versionadded:: 1.8.2

    '''
    decorator = _autoretry(
        max_tries=max_tries,
        max_time=max_time,
        wait=wait,
        retry_only=retry_only
    )

    # TODO: Create __doc__ and __name__?
    def caller(fn, *args, **kwargs):
        return decorator(fn)(*args, **kwargs)

    return caller


@decorator
def _autoretry(func, max_tries=None, max_time=None, wait=DEFAULT_WAIT_INTERVAL,
               retry_only=None):
    '''Decorate `func` so that it is tried several times upon failures.

    Arguments have the same meanings as in `dispatcher`:func:.

    '''
    from xoutil.eight import callable
    from xoutil.eight.exceptions import throw
    from xoutil.future.time import monotonic as clock, sleep

    if not max_tries and not max_time:
        raise TypeError('One of tries or times must be set')

    if not retry_only:
        retry_only = (Exception, )

    if not callable(wait):
        wait = StandardWait(wait)

    def inner(*args, **kwargs):
        t = 0
        done = False
        start = clock()
        waited = None
        while not done:
            try:
                return func(*args, **kwargs)
            except retry_only as error:
                t += 1
                reached_max_tries = max_tries and t >= max_tries
                max_time_elapsed = max_time and clock() - start >= max_time
                retry = not reached_max_tries and not max_time_elapsed
                if retry:
                    waited = wait(waited)
                    sleep(waited)
                else:
                    throw(error)

    return inner


del decorator
