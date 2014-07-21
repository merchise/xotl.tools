# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.decorator.routines
#----------------------------------------------------------------------
# Copyright (c) 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-07-21

'''Helpers for co-routines-like patterns.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


from .meta import decorator


_predicates = {}


@decorator
def predicate(target, name=None):
    '''Register a predicate for :func:`bounded`.

    The `target` predicate will must a callable that accepts a single
    positional argument (the value passed to `bounded`:func:) and returns a
    object that implements the `generator protocol <342>`:pep:.

    The generator will be `sent` each value yielded by the bounded function
    and it must yield back True if the boundary condition has been reached.

    .. todo::  Fix redaction

    When the bounded function in `bounded`:func: is called all predicates will
    be called its ``next()`` method and immediately will be called its
    ``send()`` with a tuple of arguments ``(args, kwargs)`` passed to the
    bounded function.  Predicates must be ready for this double calling
    scheme.

    The predicates are allowed to signal the boundary condition has been
    reached even at the first call of ``send()``.

    .. note:: Only the value ``True`` signals the boundary condition.

    Predicates are not allowed to raise StopIteration before informing its
    boundary condition has been meet.

    The generator will be called its ``close()`` method upon termination.
    Termination happens whenever the bounded function raises StopIteration,
    any of the predicates yield True or an error occurs inside the function or
    predicates.

    See the `timed`:func: predicated for an example.

    '''
    if not name:
        from xoutil.names import nameof
        name = nameof(target, inner=True, depth=2)
    res = _predicates.setdefault(name, target)
    if res is not target:
        raise ValueError('A predicate with the name "%s" has already been'
                         ' registered')
    return target


@predicate
def timed(val):
    '''A soft-timing boundary for :func:`bounded`.

    Usage::

         @bounded(timed=timedelta(seconds=60))
         def do_something_in_abount_60s():
             while True:
                 yield

    :param val:  The amount of time to allow the execution.  If it is a number
                 is converted to a timedelta passing the value to the
                 `seconds` argument.

    '''
    from xoutil.logger import debug
    from datetime import datetime, timedelta
    if isinstance(val, timedelta):
        boundary = val
    else:
        boundary = timedelta(seconds=val)
    yield False   # Only count time after the first call to next
    start = datetime.now()
    debug('Starting to count at %r', start)
    elapsed = False
    while not elapsed:
        yield elapsed
        elapsed = datetime.now() - start >= boundary
    debug('Signaling termination at %r', datetime.now())
    yield elapsed   # Inform the boundary condition, or we're not compliant
                    # with the predicate protocol.


@predicate
def atmost(cycles):
    '''A predicate that becomes True after a given amount of cycles.'''
    passed = 0
    yield False
    while passed < cycles:
        yield False
        passed += 1
    yield True


@predicate
def pred(func):
    '''A predicate to allow lambdas a other less speciallized callabled to
    engage in the predicate protocol.

    Example::

    @bounded(pred=lambda x: True if isinstance(x, int) and x > 10 else False)
    def fibonnaci():
        a, b = 1, 1
        while True:
           yield a
           a, b = b, a + b

    '''
    data = yield False
    while not func(data):
        data = yield False
    yield True


def bounded(*preds, **namedpreds):
    '''Run a generator in a bounded context.

    The generator yields a unit of work one at a time and the bounded
    decorator may call its ``close()`` method if any of the predicates
    indicated a boundary condition.

    It is advisable not to use too many predicates specially not mixing
    time-related predicated with others.

    The order in which the predicates will be executed is not guarranted.

    If any predicate raises an exception upon initialization, it is propagated
    unchanged and the bounded generator won't stand a chance.  See
    `predicate`:func: for more details about how to write predicates.

    The bounded function returned by this decorator will return the last data
    yielded by the wrapped function, if any was produced.

    .. warning::

       Since `bounded`:func: will consume (and not re-yield) data from the
       wrapped function, you can't nest several calls to `bounded`:func:.

    Each `pred` (unnamed predicate) is simply a generator-iterator that
    complies with the predicate protocol described in `predicate`:func: or a
    callable that evaluates to a predicate.

    Each `namedpred` (nammed predicate) must have been properly registered
    with :func:`predicate`.

    This way you may choose to use named or unnamed as you please.  The
    following signature are equivalent: ``bounded(atmost=8)`` and
    ``bounded(atmost(8))``.

    '''
    if not preds and not namedpreds:
        raise TypeError('At least a predicated must be set')
    from types import GeneratorType
    try:
        predgens = [
            pred if isinstance(pred, GeneratorType) else pred()
            for pred in preds
        ]
        if not all(isinstance(pred, GeneratorType) for pred in predgens):
            raise TypeError('There are invalid (not a generator) unnamed '
                            'predicates.')
        predgens.extend(
            _predicates[name](val)
            for name, val in namedpreds.items()
        )
    except KeyError as error:
        key = getattr(error, 'message', None)
        if key:
            raise TypeError('Invalid predicate "%s"' % key)
        else:
            raise TypeError('Invalid predicate in "%r"' % preds.keys())

    def bounder(func):
        from functools import wraps

        @wraps(func)
        def target(*args, **kwargs):
            from xoutil import Undefined
            generator = func(*args, **kwargs)
            stop, uninitialized, data = False, list(predgens), Undefined
            while not stop and uninitialized:
                pred = uninitialized.pop(0)
                try:
                    next(pred)
                    stop = stop or pred.send((args, kwargs))
                except StopIteration:
                    from xoutil.names import nameof
                    raise RuntimeError(
                        'Predicate %r is not compliant' % nameof(
                            pred, full=True
                        )
                    )
            try:
                while not stop:
                    try:
                        data = next(generator)
                    except (GeneratorExit, StopIteration):
                        stop = True
                    else:
                        try:
                            # XXX: Can't use any(...) here cause it will
                            # swallow StopIteration from pred.send()
                            i, top = 0, len(predgens)
                            while not stop and i < top:
                                pred = predgens[i]
                                stop = pred.send(data)
                                i += 1
                        except StopIteration:
                            from xoutil.names import nameof
                            raise RuntimeError(
                                'Predicate %r is not compliant' % nameof(
                                    pred, full=True
                                )
                            )
            finally:
                generator.close()
                for pred in predgens:
                    pred.close()
            if data is not Undefined:
                return data
        return target
    return bounder
