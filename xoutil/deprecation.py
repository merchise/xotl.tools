#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.deprecation
#----------------------------------------------------------------------
# Copyright (c) 2012 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on Feb 15, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

__docstring_format__ = 'rst'
__author__ = 'manu'

def deprecated(replacement, msg='{funcname} is now deprecated and it will be removed. Use {replacement} instead'):
    'Small decorator for deprecated functions'
    def decorator(target):
        import warnings
        from functools import wraps
        funcname = target.__name__
        if isinstance(target, type):
            def init(self, *args, **kwargs):
                warnings.warn(msg.format(funcname=funcname, replacement=replacement))
                return super(target, self).__init__(*args, **kwargs)
            klass = type(target.__name__, (target,), {'__init__': init})
            return klass
        else:
            @wraps(target)
            def inner(*args, **kw):
                warnings.warn(msg.format(funcname=funcname, replacement=replacement),
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
        import inspect
        frame, filename, lineno, funcname, lines, indx = inspect.stack()[-1]
        try:
            target_locals = frame.f_locals
        finally:
            # As recommeded to avoid memory leaks
            del frame, filename, lineno, funcname, lines, indx
    else:
        # TODO: Allow this
        pass
    for funcname in funcnames:
        func = getattr(source, funcname, None)
        if func:
            target_locals[funcname] = deprecated(source.__name__ + '.' + funcname)(func)
        else:
            import warnings
            warnings.warn('{funcname} was expected to be in {source}'.
                          format(funcname=funcname, source=source.__name__))
