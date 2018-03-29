#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Helpers for bounded execution of co-routines.

Example::

    >>> def fibonacci():
    ...   a, b = 1, 1
    ...   while True:
    ...       yield a
    ...       a, b = b, a + b

This function yields forever.  This module allows to get instances of that
function that run until a boundary condition is met.  For instance, the
`times`:func: boundary stops after a given numbers of results are generated::

    >>> fib8 = times(8)(fibonacci)
    >>> fib8()   # the 8th fibonacci number is
    21

This is repeatable::

    >>> fib8()   # the 8th fibonacci number is
    21

    >>> fib8()   # the 8th fibonacci number is
    21

Unless you pass in a generator::

    >>> fib8 = times(8)(fibonacci())
    >>> fib8()
    21

    >>> fib8() is None
    True

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from types import GeneratorType
from xoutil.decorator.meta import decorator


class BoundedType(type):
    '''A bounded generator/function.'''
    pass


class Bounded(metaclass=BoundedType):
    '''The bounded function.

    This is the result of applying a `boundary definition` to an `unbounded
    function` (or generator).

    If `target` is a function this instance can be called several times.  If
    it's a generator then it will be closed after either calling
    (``__call__``) this instance, or consuming the generator given by
    `generate`:meth:.

    '''
    def __init__(self, target):
        self.target = target

    # The following two methods are actually implemented as closures in the
    # apply method of BoundaryCondition.  Nevertheless, they are documented
    # here as an API promise.
    def __call__(self, *args, **kwargs):
        '''Return the last value from the underlying `bounded generator`.

        '''
        raise NotImplementedError()

    def generate(self, *args, **kwargs):
        '''Return the `bounded generator`.

        This method exposes the `bounded generator`.  This allows you to "see"
        all the values yielded by the `unbounded generator` up to the point
        when the boundary condition is met.

        '''
        raise NotImplementedError()


class BoundaryCondition:
    '''Embodies the boundary protocol.

    The `definition` argument must a function that implements a `boundary
    definition`.  This function may take arguments to initialize the state of
    the boundary condition.

    Instances are callables that will return a `Bounded`:class: subclass
    specialized with the application of the `boundary condition` to a given
    unbounded function (`target`).  For instance, ``times(6)`` returns a
    class, that when instantiated with a `target` represents the bounded
    function that takes the 6th valued yielded by target.

    If the `definition` takes no arguments for initialization you may pass the
    `target` directly.  This is means that if `__call__`:func: receives
    arguments they will be used to instantiate the `Bounded`:class: subclass,
    ie. this case allows only a single argument `target`.

    If `errors` is not None it should be a tuple of exceptions to catch and
    throw inside the boundary condition definition.  Other exceptions, beside
    GeneratorExit and StopIteration, are not handled (so the bubble up).  See
    `until_error`:func:.

    '''
    def __new__(cls, definition, name=None, errors=None):
        from types import FunctionType
        if not isinstance(definition, FunctionType):
            raise TypeError('"definition" must be a function')
        if not name:
            from xoutil.names import nameof
            name = nameof(definition, inner=True, full=True)
        result = super().__new__(cls)
        result.name = name  # needs to be set here or it'll be None
        return result

    def __init__(self, definition, name=None, errors=None):
        from inspect import getargspec
        spec = getargspec(definition)
        self.args = spec[0]
        self.defaults = spec[3]
        self.varargs = spec[1]
        self.varkwargs = spec[2]
        self.definition = definition
        if not errors:
            errors = (Exception, )
        self.errors = errors

    def __str__(self):
        return str('boundary %s(...)' % self.name)

    def __repr__(self):
        return str(self)

    @property
    def receive_args(self):
        return self.args or self.defaults or self.varargs or self.varkwargs

    def apply(self, args, kwargs):
        def execute(boundary, unbounded, initial):
            '''Executes the unbounded generator guarded by a boundary condition.

            `boundary` is the boundary condition. `unbounded` is the unbounded
            generator.  Both must be generators.

            `initial` is the tuple of ``(args, kwargs)`` passed when calling
            the unbounded function or None.

            This function is used in the (closure) `generate` method of the
            Bounded subclass returned by `apply`.  It contains the core
            algorithm that interleaves the boundary condition with the
            unbounded generator.

            '''
            try:
                next(boundary)  # Initialize the boundary condition
                stop = boundary.send(initial)
            except StopIteration:
                raise RuntimeError(
                    'Invalid boundary definition "%r"' % self.definition
                )
            try:
                while stop is not True:
                    try:
                        data = next(unbounded)
                        yield data
                    except (GeneratorExit, StopIteration):
                        stop = True
                    except self.errors as error:
                        stop = boundary.throw(error)
                    else:
                        try:
                            stop = boundary.send(data)
                        except StopIteration:
                            raise RuntimeError(
                                'Invalid boundary definition "%r"' %
                                self.definition
                            )
            finally:
                boundary.close()
                unbounded.close()

        class bounded(Bounded):
            @classmethod
            def build_pred(boundedcls):
                return self.build_generator(args, kwargs)

            def generate(me, *args, **kwargs):
                target = me.target
                if isinstance(target, GeneratorType):
                    return execute(me.build_pred(), target, None)
                else:
                    generator = target(*args, **kwargs)
                    return execute(me.build_pred(), generator, (args, kwargs))

            def __call__(me, *args, **kwargs):
                data = None
                for data in me.generate(*args, **kwargs):
                    pass
                return data

        return bounded  # return from apply()

    def build_generator(self, args, kwargs):
        if self.receive_args:
            generator = self.definition(*args, **kwargs)
        else:
            generator = self.definition()
        return generator

    def __call__(self, *args, **kwargs):
        if self.receive_args:
            return self.apply(args, kwargs)
        elif args or kwargs:
            result = self.apply((), {})(*args, **kwargs)
            if len(args) == 1:
                from functools import update_wrapper
                update_wrapper(result, args[0])
            return result
        else:
            return self.apply((), {})


@decorator
def boundary(definition, name=None, base=BoundaryCondition, errors=None):
    '''Helper to define a boundary condition.

    The `definition` must be a function that returns a generator.  The
    following rules **must be** followed.  Collectively these rules are called
    the `boundary protocol`.

    - The `boundary definition` will yield True when and only when the
      boundary condition is met.  Only the value True will signal the boundary
      condition.

    - The `boundary definition` must yield at least 2 times:

      - First it will be called its ``next()`` method to allow for
        initialization of internal state.

      - Immediately after, it will be called its ``send()`` passing the tuple
        ``(args, kwargs)`` with the arguments passed to the `unbounded
        function`.  At this point the boundary definition may yield True to
        halt the execution.  In this case, the `unbounded generator` won't be
        asked for any value.

    - The `boundary definition` must yield True before terminating with a
      StopIteration.  For instance the following definition is invalid cause
      it ends without yielding True::

          @boundary
          def invalid():
              yield
              yield False

    - The `boundary definition` must deal with GeneratorExit exceptions
      properly since we call the ``close()`` method of the generator upon
      termination.  Termination occurs when the `unbounded generator` stops by
      any means, even when the boundary condition yielded True or the
      generator itself is exhausted or there's an error in the generator.

      Both `whenall`:func: and `whenany`:func: call the ``close()`` method of
      all their subordinate boundary conditions.

      Most of the time this reduces to *not* catching GeneratorExit
      exceptions.

    A RuntimeError may happen if any of these rules is not followed by the
    `definition`.  Furthermore, this error will occur when invoking the
    `bounded function` and not when applying the boundary to the `unbounded
    generator`.

    '''
    from functools import update_wrapper
    result = base(definition, name=name, errors=errors)
    return update_wrapper(result, definition)


@boundary
def timed(maxtime):
    '''Becomes True after a given amount of time.

    The bounded generator will be allowed to yields values until the `maxtime`
    time frame has elapsed.

    Usage::

         @timed(timedelta(seconds=60))
         def do_something_in_about_60s():
             while True:
                 yield

    .. note:: This is a very soft limit.

       We can't actually guarrant any enforcement of the time limit.  If the
       bounded generator takes too much time or never yields this predicated
       can't do much.  This usually helps with batch processing that must not
       exceed (by too much) a given amount of time.

    The timer starts just after the ``next()`` function has been called for
    the predicate initialization.  So if the `maxtime` given is too short this
    predicated might halt the execution of the bounded function without
    allowing any processing at all.

    If `maxtime` is not a timedelta, the timedelta will be computed as
    ``timedelta(seconds=maxtime)``.

    '''
    from datetime import datetime, timedelta
    if isinstance(maxtime, timedelta):
        bound = maxtime
    else:
        bound = timedelta(seconds=maxtime)
    start = datetime.now()
    yield False  # Deal with next-send calling scheme for boundaries
    while datetime.now() - start < bound:
        yield False
    yield True   # Or we're not compliant with the boundary protocol.


@boundary
def times(n):
    '''Becomes True after a given after the `nth` item have been produced.'''
    passed = 0
    yield False
    while passed < n:
        yield False
        passed += 1
    yield True


@boundary
def accumulated(mass, *attrs, **kwargs):
    '''Becomes True after accumulating a given "mass".

    `mass` is the maximum allowed to accumulate.  This is usually a positive
    number.  Each value produced by the `unbounded generator` is added
    together.  Yield True when this amount to more than the given `mass`.

    If any `attrs` are provided, they will be considered attributes (or keys)
    to search inside the yielded data from the bounded function.  If no
    `attrs` are provided the whole data is accumulated, so it must allow
    addition.  The attribute to be summed is extracted with
    `~xoutil.objects.get_first_of`:func:, so only the first attribute found is
    added.

    If the keyword argument `initial` is provided the accumulator is
    initialized with that value.  By default this is 0.

    '''
    from xoutil.objects import get_first_of
    accum = kwargs.pop('initial', 0)
    if kwargs:
        raise TypeError('Invalid keyword arguments %r' % kwargs.keys())
    yield False
    while accum < mass:
        data = yield False
        accum += get_first_of(data, *attrs, default=data)
    yield True


@boundary
def pred(func, skipargs=True):
    '''Allow "normal" functions to engage within the boundary protocol.

    `func` should take a single argument and return True if the boundary
    condition has been met.

    If `skipargs` is True then function `func` will not be called with the
    tuple ``(args, kwargs)`` upon initialization of the boundary, in that case
    only yielded values from the `unbounded generator` are passed.  If you
    need to get the original arguments, set `skipargs` to False, in this case
    the first time `func` is called will be passed a single argument ``(arg,
    kwargs)``.

    Example::

      >>> @pred(lambda x: x > 10)
      ... def fibonacci():
      ...     a, b = 1, 1
      ...     while True:
      ...        yield a
      ...        a, b = b, a + b

      >>> fibonacci()
      13

    '''
    sentinel = object()
    data = yield False
    if skipargs:
        data = sentinel
    while data is sentinel or not func(data):
        data = yield False
    yield True


def until_errors(*errors, **kwargs):
    '''Becomes True after any of `errors` has been raised.

    Any other exceptions (except GeneratorExit) is propagated.  You must pass
    at least an error.

    Normally this will allow some possibly long jobs to be interrupted
    (SoftTimeLimitException in celery task, for instance) but leave some time
    for the caller to clean up things.

    It's assumed that your job can be properly *finalized* after any of the
    given exceptions has been raised.

    :keyword on_error: A callable that will only be called if the boundary
                       condition is ever met, i.e if any of `errors` was
                       raised.  The callback is called before yielding True.

    .. versionadded:: 1.7.2

    .. versionchanged:: 1.7.5 Added the keyword argument `on_error`.

    '''
    if not errors:
        raise TypeError('catch must be called with at least an exception')
    elif any(not issubclass(e, Exception) for e in errors):
        raise TypeError(
            'catch must be called only with subclasses of Exception'
        )
    if any(issubclass(e, GeneratorExit) for e in errors):
        raise TypeError('You cannot catch GeneratorExit')
    on_error = kwargs.pop('on_error', None)
    if kwargs:
        raise TypeError('Invalid keyword arguments: %s' % ', '.join(kwargs))

    @boundary(errors=errors)
    def _catch():
        yield False
        try:
            while True:
                yield False
        except errors:
            if on_error is not None:
                on_error()
            yield True
    return _catch()


def until(**kwargs):
    '''An idiomatic alias to other boundary definitions.

    - ``until(maxtime=n)`` is the same as ``timed(n)``.

    - ``until(times=n)`` is the same as ``times(n)``.

    - ``until(pred=func, skipargs=skip)`` is the same as
      ``pred(func, skipargs=skip)``.

    - ``until(errors=errors, **kwargs)`` is the same as
      ``until_errors(*errors, **kwargs)``.

    - ``until(accumulate=mass, path=path, initial=initial)`` is the same as
       ``accumulated(mass, *path.split('.'), initial=initial)``

    .. warning:: You cannot mix many calls.

    .. versionadded:: 1.7.2

    '''
    maxtime = kwargs.pop('maxtime', None)
    if maxtime:
        return timed(maxtime, **kwargs)
    n = kwargs.pop('times', None)
    if n:
        return times(n, **kwargs)
    func = kwargs.pop('pred', None)
    if func:
        return pred(func, **kwargs)
    errors = kwargs.pop('errors', None)
    if errors:
        return until_errors(*errors, **kwargs)
    mass = kwargs.pop('accumulate', None)
    if mass:
        path = kwargs.pop('path', None)
        if path:
            return accumulated(mass, *path.split('.'), **kwargs)
        else:
            return accumulated(mass, **kwargs)
    raise TypeError


class HighLevelBoundary(BoundaryCondition):
    '''Boundary class for high-level boundary conditions.

    The `apply` method of this only accepts the `args`, which must be
    BoundaryCondition objects or BoundedType objects (ie. an instance of a
    boundary condition), then it replaces the normal boundary condition for
    that of the high-level given the subordinate definitions.

    '''

    def apply(self, boundaries, kwargs):
        assert boundaries and not kwargs
        base = super().apply(boundaries, kwargs)

        class rebounded(base):
            @classmethod
            def build_pred(cls):
                from types import FunctionType, GeneratorType
                subordinates = []
                for bound in boundaries:
                    if isinstance(bound, FunctionType):
                        bound = boundary(bound)
                    elif isinstance(bound, GeneratorType):
                        gen = bound  # get a copy for the lambda below
                        bound = boundary(lambda: gen)
                    if isinstance(bound, BoundaryCondition):
                        if bound.receive_args:
                            raise TypeError(
                                '"%s" must be initialized' % bound.name
                            )
                        bound = bound.apply((), {})
                    if isinstance(bound, BoundedType):
                        sub = bound.build_pred()
                    else:
                        raise TypeError('Invalid argument "%r"' % bound)
                    subordinates.append(sub)
                return self.definition(*subordinates)
        return rebounded


@boundary(base=HighLevelBoundary)
def whenall(*subordinates):
    '''An AND-like boundary condition.

    It takes several boundaries and returns a single one that behaves like the
    logical AND i.e, will yield True when **all** of its subordinate boundary
    conditions have yielded True.

    It ensures that once a subordinate yields True it won't be sent more data,
    no matter if other subordinates keep on running and consuming data.

    Calls ``close()`` of all subordinates upon termination.

    Each `boundary` should be either:

    - A "bare" boundary definition that takes no arguments.

    - A boundary condition (i.e an instance of `BoundaryCondition`:class:).
      This is result of calling a boundary definition.

    - A generator object that complies with the boundary protocol.  This
      cannot be tested upfront, a misbehaving generator will cause a
      RuntimeError if a boundary protocol rule is not followed.

    Any other type is a TypeError.

    '''
    preds = list(subordinates)  # a copy of the list
    for pred in preds:
        next(pred)
    try:
        while preds:  # out of preds it means all have yielded True
            data = yield False
            i = 0
            while preds and i < len(preds):
                pred = preds[i]
                try:
                    res = pred.send(data)
                except StopIteration:
                    raise RuntimeError('Invalid predicated in %r' % preds)
                else:
                    if res is True:
                        del preds[i]  # no more send() for this pred
                    else:
                        i += 1
        yield True
    except GeneratorExit:
        pass
    for pred in subordinates:
        pred.close()


@boundary(base=HighLevelBoundary)
def whenany(*preds):
    '''An OR-like boundary condition.

    It takes several boundaries and returns a single one that behaves like the
    logical OR, i.e, will yield True when **any** of its subordinate boundary
    conditions yield True.

    Calls ``close()`` of all subordinates upon termination.

    Each `boundary` should be either:

    - A "bare" boundary definition that takes no arguments.

    - A boundary condition (i.e an instance of `BoundaryCondition`:class:).
      This is result of calling a boundary definition.

    - A generator object that complies with the boundary protocol.  This
      cannot be tested upfront, a misbehaving generator will cause a
      RuntimeError if a boundary protocol rule is not followed.

    Any other type is a TypeError.

    '''
    for pred in preds:
        next(pred)
    stop = False
    try:
        while stop is not True:
            data = yield stop
            i, top = 0, len(preds)
            while not stop and i < top:
                pred = preds[i]
                try:
                    stop = stop or pred.send(data)
                except StopIteration:
                    raise RuntimeError('Invalid predicated in %r' % preds)
                else:
                    i += 1
        yield stop
    except GeneratorExit:
        pass
    for pred in preds:
        pred.close()


del decorator
