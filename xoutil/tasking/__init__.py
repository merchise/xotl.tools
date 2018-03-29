#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Task, multitasking, and concurrent programming tools.

.. warning:: Experimental.  API is not settled.

.. versionadded:: 1.8.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import sys
from xoutil.deprecation import deprecated


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
        super().__init__()
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


class ConstantWait:
    '''A constant wait algorithm.

    Instances are callables that comply with the need of the `wait` argument
    for `retrier`:class:.  This callable always return the same `wait` value.

    We never wait less than `MIN_WAIT_INTERVAL`:data:.

    .. versionadded:: 1.8.2

    .. versionchanged:: 1.9.1 Renamed; it was ``StandardWait``.  The old name
       is kept as a deprecated alias.

    .. versionchanged:: 2.0.1 Renamed; it was ``StandardWait``.  The old name
       is kept as a deprecated alias.

    '''
    def __init__(self, wait=DEFAULT_WAIT_INTERVAL):
        import numbers
        if not isinstance(wait, numbers.Real):
            raise TypeError("'wait' must a number.")
        self.wait = max(MIN_WAIT_INTERVAL, wait)

    def __call__(self, prev=None):
        return self.wait


StandardWait = deprecated(
    ConstantWait,
    'StandardWait is deprecated. Use ConstantWait instead'
)(ConstantWait)


class BackoffWait:
    '''A wait algorithm with an exponential backoff.

    Instances are callables that comply with the need of the `wait` argument
    for `retrier`:class:.

    At each call the wait is increased by doubling `backoff` (given in
    milliseconds).

    We never wait less than `MIN_WAIT_INTERVAL`:data:.

    .. versionadded:: 1.8.2

    '''
    def __init__(self, wait=DEFAULT_WAIT_INTERVAL, backoff=1):
        self.wait = max(MIN_WAIT_INTERVAL, wait)
        self.backoff = min(max(0.1, backoff), 1)

    def __call__(self, prev=None):
        res = self.wait + (self.backoff / 1000)
        self.backoff = self.backoff * 2
        return res


def retry(fn, args=None, kwargs=None, *, max_tries=None, max_time=None,
          wait=DEFAULT_WAIT_INTERVAL, retry_only=None):
    '''Run `fn` with args and kwargs in an auto-retrying loop.

    See `retrier`:class:.  This is just::

       >>> retrier(max_tries=max_tries, max_time=max_time, wait=wait,
       ...         retry_only=retry_only)(fn, *args, **kwargs)

    .. versionadded:: 1.8.2

    '''
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    return retrier(max_tries=max_tries, max_time=max_time, wait=wait,
                   retry_only=retry_only)(fn, *args, **kwargs)


class retrier:
    '''An auto-retrying dispatcher.

    A retrier it's a callable that takes another callable (`func`) and its
    arguments and runs it in an auto-retrying loop.

    If `func` raises any exception that is in `retry_only`, and it has being
    tried less than `max_tries` and the time spent executing the function
    (waiting included) has not reached `max_time`, the function will be
    retried.

    `wait` can be a callable or a number.  If `wait` is callable, it must take
    a single argument with the previous waiting we did (`None`:data: for the
    first retry) and return the number of seconds to wait before retrying.

    If `wait` is a number, we convert it to a callable with
    `ConstantWait(wait) <ConstantWait>`:class:.

    .. seealso:: `BackoffWait`:class:

    If `retry_only` is None, all exceptions (that inherits from Exception)
    will be retried.  Otherwise, only the exceptions in `retry_only` will be
    retried.

    Waiting is done with `time.sleep`:func:.  Time tracking is done with
    `time.monotonic`:func:.

    .. versionadded:: 1.8.2

    '''
    def __init__(self, max_tries=None, max_time=None,
                 wait=DEFAULT_WAIT_INTERVAL, retry_only=None):
        from xoutil.eight import callable
        if not max_tries and not max_time:
            raise TypeError('One of tries or times must be set')
        self.max_tries = max_tries
        self.max_time = max_time
        if not callable(wait):
            self.wait = ConstantWait(wait)
        else:
            self.wait = wait
        if not retry_only:
            self.retry_only = (Exception, )
        else:
            self.retry_only = retry_only

    def __call__(self, fn, *args, **kwargs):
        return self.decorate(fn)(*args, **kwargs)

    def decorate(self, fn):
        '''Return `fn` decorated to run in an auto-retry loop.

        You can use this to decorate a function you'll always run inside a
        retrying loop:

           >>> @retrier(max_tries=5, retry_only=TransientError).decorate
           ... def read_from_url(url):
           ...     pass

        '''
        from xoutil.future.time import monotonic as clock, sleep
        from xoutil.future.functools import wraps
        max_time = self.max_time
        max_tries = self.max_tries

        @wraps(fn)
        def inner(*args, **kwargs):
            t = 0
            done = False
            start = clock()
            waited = None
            while not done:
                try:
                    return fn(*args, **kwargs)
                except self.retry_only as error:
                    t += 1
                    reached_max_tries = max_tries and t >= max_tries
                    max_time_elapsed = max_time and clock() - start >= max_time
                    retry = not reached_max_tries and not max_time_elapsed
                    if retry:
                        waited = self.wait(waited)
                        sleep(waited)
                    else:
                        raise

        return inner


del deprecated
