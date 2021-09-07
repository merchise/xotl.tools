#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""Decorator-making facilities.

This module provides a signature-keeping version of the
`xotl.tools.decorators.decorator`:func:, which is now deprecated in favor of
this module's version.

We scinded the decorator-making facilities from decorators per se to allow the
module `xotl.tools.deprecation`:mod: to be used by decorators and at the same
time, implement the decorator `~xotl.tools.deprecation.deprecated`:func: more
easily.

"""
from functools import partial, wraps
from types import FunctionType as function

__all__ = ("decorator",)


def decorator(caller):
    """Eases the creation of decorators with arguments.  Normally a decorator
    with arguments needs three nested functions like this::

        def decorator(*decorator_arguments):
            def real_decorator(target):
                def inner(*args, **kwargs):
                    return target(*args, **kwargs)
                return inner
            return real_decorator

    This decorator reduces the need of the first level by comprising both into
    a single function definition. However it does not removes the need for an
    ``inner`` function::

        >>> @decorator
        ... def plus(target, value):
        ...    from functools import wraps
        ...    @wraps(target)
        ...    def inner(*args):
        ...        return target(*args) + value
        ...    return inner

        >>> @plus(10)
        ... def ident(val):
        ...     return val

        >>> ident(1)
        11

    A decorator with default values for all its arguments (except, of course,
    the first one which is the decorated `target`) may be invoked
    without parenthesis::

        >>> @decorator
        ... def plus2(func, value=1, missing=2):
        ...    from functools import wraps
        ...    @wraps(func)
        ...    def inner(*args):
        ...        print(missing)
        ...        return func(*args) + value
        ...    return inner

        >>> @plus2
        ... def ident2(val):
        ...     return val

        >>> ident2(10)
        2
        11

    But (if you like) you may place the parenthesis::

        >>> @plus2()
        ... def ident3(val):
        ...     return val

        >>> ident3(10)
        2
        11

    However, this is not for free, you cannot pass a single positional argument
    which type is a function::

        >>> def p():
        ...    print('This is p!!!')

        >>> @plus2(p)   # doctest: +ELLIPSIS
        ... def dummy():
        ...    print('This is dummy')
        Traceback (most recent call last):
            ...
        TypeError: p() takes ...

    The workaround for this case is to use a keyword argument.

    """

    @wraps(caller)
    def outer_decorator(*args, **kwargs):
        try:
            from zope.interface import Interface
        except ImportError:
            Interface = None
            # from xotl.tools.symbols import Unset as Interface
        if (
            len(args) == 1
            and not kwargs
            and (
                isinstance(args[0], (function, type)) or issubclass(type(args[0]), type(Interface))
            )
        ):
            # This tries to solve the case of missing () on the decorator::
            #
            #    @decorator
            #    def somedec(func, *args, **kwargs)
            #        ...
            #
            #    @somedec
            #    def decorated(*args, **kwargs):
            #        pass
            #
            # Notice, however, that this is not general enough, since we try
            # to avoid inspecting the calling frame to see if the () are in
            # place.
            func = args[0]
            return caller(func)
        elif len(args) > 0 or len(kwargs) > 0:

            def _decorator(func):
                return partial(caller, **kwargs)(*((func,) + args))

            return _decorator
        else:
            return caller

    return outer_decorator
