#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.deprecation
#----------------------------------------------------------------------
# Copyright (c) 2012 Merchise Autrement
# All rights reserved.
#
# Author: Manuel Vázquez Acosta
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Feb 15, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

import types
import warnings

from functools import wraps


__docstring_format__ = 'rst'
__author__ = 'manu'


DEFAULT_MSG = ('{funcname} is now deprecated and it will be removed. ' +
              'Use {replacement} instead.')


def deprecated(replacement, msg=DEFAULT_MSG, deprecated_module=None):
    '''Small decorator for deprecated functions.

    Usage::

        @deprecate(new_function)
        def deprecated_function(...):
            ...

    '''
    def decorator(target):
        if deprecated_module:
            funcname = deprecated_module + '.' + target.__name__
        else:
            funcname = target.__name__
        if isinstance(replacement, types.FunctionType):
            repl_name = replacement.__module__ + '.' + replacement.__name__
        else:
            repl_name = replacement
        if isinstance(target, (type, types.TypeType)):
            def new(*args, **kwargs):
                warnings.warn(msg.format(funcname=funcname,
                                         replacement=repl_name),
                              stacklevel=2)
                return target.__new__(*args, **kwargs)
            klass = type(target.__name__, (target,), {'__new__': new})
            return klass
        else:
            @wraps(target)
            def inner(*args, **kw):
                warnings.warn(msg.format(funcname=funcname,
                                         replacement=repl_name),
                              stacklevel=2)
                return target(*args, **kw)
            return inner
    return decorator


def inject_deprecated(funcnames, source, target=None):
    '''
    Takes a sequence of function names `funcnames` which reside in the `source`
    module and injects them into `target` marked as deprecated. If `target` is
    None then we inject the functions into the locals of the calling code. It's
    expected it's a module.

    This function is provided for easing the deprecation of whole modules and
    should not be used to do otherwise.
    '''
    if not target:
        import sys
        frame = sys._getframe(1)
        try:
            target_locals = frame.f_locals
        finally:
            # As recommeded to avoid memory leaks
            del frame
    else:
        pass
    for targetname in funcnames:
        target = getattr(source, targetname, None)
        if target:
            if isinstance(target, (type, types.FunctionType, types.LambdaType,
                                   types.ClassType, types.TypeType)):
                replacement = source.__name__ + '.' + targetname
                module_name = target_locals.get('__name__', None)
                target_locals[targetname] = deprecated(replacement,
                                                       DEFAULT_MSG,
                                                       module_name)(target)
            else:
                target_locals[targetname] = target
        else:
            warnings.warn('{targetname} was expected to be in {source}'.
                          format(targetname=targetname,
                                 source=source.__name__), stacklevel=2)
