#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""Extensions to the `functools` module from the Python's standard library.

You may use this module as drop-in replacement of `functools`.

"""
from functools import *  # noqa
from functools import _CacheInfo  # noqa


# TODO: Check relevance of the following function.
# The real signature should be (*funcs, times)
def power(*args):
    """Returns the "power" composition of several functions.

    Examples::

       >>> import operator
       >>> f = power(partial(operator.mul, 3), 3)
       >>> f(23) == 3*(3*(3*23))
       True

       >>> power(operator.neg)
       Traceback (most recent call last):
       ...
       TypeError: power() takes at least 2 arguments (1 given)

    """
    from xotl.tools.fp.tools import compose
    from xotl.tools.params import check_count

    check_count(args, 2, caller="power")
    *funcs, times = args
    if any(not callable(func) for func in funcs):
        raise TypeError("Arguments of `power`, but last, must be callables")
    if not (isinstance(times, int) and times > 0):
        raise TypeError("Last argument of `power` must be a positive integer")
    if len(funcs) > 1:
        base = (compose(funcs),)
    else:
        base = (funcs[0],)
    return compose(*(base * times))


def lwraps(*args, **kwargs):
    """Lambda wrapper.

    Useful for decorate lambda functions with name and documentation.

    As positional arguments could be passed the function to be decorated and
    the name in any order.  So the next two ``identity`` definitions are
    equivalents::

      >>> from xotl.tools.future.functools import lwraps as lw

      >>> identity = lw('identity', lambda arg: arg)

      >>> identity = lw(lambda arg: arg, 'identity')

    As keyword arguments could be passed some special values, and any number
    of literal values to be assigned:

    - **name**: The name of the function (``__name__``); only valid if not
      given as positional argument.

    - **doc**: The documentation (``__doc__`` field).

    - **wrapped**: An object to extract all values not yet assigned.  These
      values are ('__module__', '__name__' and '__doc__') to be assigned, and
      '__dict__' to be updated.

    If the function to decorate is present in the positional arguments, this
    same argument function is directly returned after decorated; if not a
    decorator is returned similar to standard `wraps`:func:.

    For example::

      >>> from xotl.tools.future.functools import lwraps as lw

      >>> is_valid_age = lw('is-valid-human-age', lambda age: 0 < age <= 120,
      ...                   doc=('A predicate to evaluate if an age is '
      ...                        'valid for a human being.')

      >>> @lw(wrapped=is_valid_age)
      ... def is_valid_working_age(age):
      ...     return 18 < age <= 70

      >>> is_valid_age(16)
      True

      >>> is_valid_age(200)
      False

      >>> is_valid_working_age(16)
      False

    .. versionadded:: 1.7.0

    """
    from types import FunctionType, MethodType

    from xotl.tools.params import check_count
    from xotl.tools.symbols import Unset

    def repeated(name):
        msg = "lwraps got multiple values for argument '{}'"
        raise TypeError(msg.format(name))

    def settle_str(name, value):
        if value is not Unset:
            if isinstance(value, str):
                if name not in source:
                    source[name] = value
                else:
                    repeated(name)
            else:
                msg = 'lwraps expecting string for "{}", {} found'
                raise TypeError(msg.format(name, type(value).__name__))

    methods = (staticmethod, classmethod, MethodType)
    decorables = methods + (FunctionType,)

    name_key = "__name__"
    doc_key = "__doc__"
    mod_key = "__module__"
    safes = {name_key, mod_key}
    source = {}
    target = Unset
    count = len(args)
    check_count(count, 0, 2, caller="lwraps")
    i = 0
    while i < count:
        arg = args[i]
        if isinstance(arg, str):
            settle_str(name_key, arg)
        elif isinstance(arg, decorables):
            if target is Unset:
                target = arg
            else:
                repeated("target-function")
        else:
            msg = "lwraps arg {} must be a string or decorable function"
            raise TypeError(msg.format(i))
        i += 1
    wrapped = kwargs.pop("wrapped", Unset)
    settle_str(name_key, kwargs.pop("name", Unset))
    settle_str(name_key, kwargs.pop(name_key, Unset))
    settle_str(doc_key, kwargs.pop("doc", Unset))
    settle_str(doc_key, kwargs.pop(doc_key, Unset))
    source.update(kwargs)
    if wrapped is not Unset:
        # TODO: Check the type of `wrapped` to find these attributes in
        # disparate callable objects similarly with functions.
        for name in (mod_key, name_key, doc_key):
            if name not in source:
                source[str(name)] = getattr(wrapped, name)
        d = source.setdefault("__dict__", {})
        d.update(wrapped.__dict__)

    def wrapper(target):
        if isinstance(target, decorables):
            res = target
            if isinstance(target, methods):
                target = target.__func__
            for name in (mod_key, name_key, doc_key):
                if name in source:
                    value = source.pop(name)
                    if name in safes:
                        value = str(value)
                    setattr(target, str(name), value)
                d = source.pop("__dict__", Unset)
                if d:
                    target.__dict__.update(d)
            for key in source:
                setattr(target, key, source[key])
            return res
        else:
            msg = "only functions are decorated, not {}"
            raise TypeError(msg.format(type(target).__name__))

    return wrapper(target) if target else wrapper

    # TODO: Next code could be removed.
    # func.__name__ = string.force(name)
    # if doc:
    #     func.__doc__ = doc
    # return func


def curry(f):
    """Return a function that automatically 'curries' is positional arguments.

    Example::

        >>> add = curry(lambda x, y: x + y)
        >>> add(1)(2)
        3

        >>> add(1, 2)
        3

        >>> add()()()(1, 2)
        3
    """
    from xotl.tools.future.inspect import getfullargspec

    fargs = getfullargspec(f)[0]

    def curried(cargs=None):
        if cargs is None:
            cargs = []

        def inner(*args, **kwargs):
            cargs_ = cargs + list(args)
            if len(cargs_) < len(fargs):
                return curried(cargs_)
            else:
                return f(*cargs_, **kwargs)

        return inner

    return curried()
