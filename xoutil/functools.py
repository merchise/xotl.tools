#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.functools
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
# Created on Feb 22, 2012

'''
The `functools` module is for higher-order functions: functions that act on or
return other functions. In general, any callable object can be treated as a
function for the purposes of this module.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

__docstring_format__ = 'rst'
__author__ = 'manu'

import functools as _legacy
#~ from functools import partial, update_wrapper
#~ partial = _legacy.partial
#~ update_wrapper = _legacy.update_wrapper

# The following copies all from _legacy to the current module
from xoutil.data import smart_copy
smart_copy(_legacy , __import__(__name__, fromlist=[b'_legacy']))
del smart_copy


WRAPPER_ASSIGNMENTS = ('__module__', '__name__')
WRAPPER_UPDATES = ('__dict__',)
_update_wrapper = update_wrapper

def update_wrapper(wrapper,
                   wrapped,
                   assigned=WRAPPER_ASSIGNMENTS,
                   updated=WRAPPER_UPDATES,
                   add_signature=False):
    """Update a wrapper function to look like the wrapped function

       wrapper is the function to be updated
       wrapped is the original function
       assigned is a tuple naming the attributes assigned directly
       from the wrapped function to the wrapper function (defaults to
       functools.WRAPPER_ASSIGNMENTS)
       updated is a tuple naming the attributes of the wrapper that
       are updated with the corresponding attribute from the wrapped
       function (defaults to functools.WRAPPER_UPDATES)

       Fixed on xoutil:

       Since most decorators use the *args, **kwargs idiom for arguments it is
       introduced the `add_signature` argument to prepend the signature to the
       documentation.
    """
    from inspect import getargspec
    result = _update_wrapper(wrapper, wrapped, assigned, updated)
    doc = getattr(wrapped, '__doc__')
    if add_signature:
        module = getattr(wrapped, '__module__')
        name = getattr(wrapped, '__name__')
        spec = getargspec(wrapped)
        rsign = []
        nargs_without_default_values = len(spec.args) - len(spec.defaults or [])
        rsign.extend(spec.args[:nargs_without_default_values])
        if spec.defaults:
            rsign.extend('{arg}={val!r}'.format(arg=spec.args[nargs_without_default_values + i],
                                                val=spec.defaults[i])
                            for i in range(len(spec.defaults)))
        if spec.varargs:
            rsign.append('*' + spec.varargs)
        if spec.keywords:
            rsign.append('**' + spec.keywords)
        signature = ', '.join(rsign)
        doc = "{module}:{name}({signature})\n\n{doc}".format(**locals())
    setattr(wrapper, '__doc__', doc)
    return result


def wraps(wrapped,
          assigned=WRAPPER_ASSIGNMENTS,
          updated=WRAPPER_UPDATES,
          add_signature=False):
    """Decorator factory to apply update_wrapper() to a wrapper function

       Returns a decorator that invokes update_wrapper() with the decorated
       function as the wrapper argument and the arguments to wraps() as the
       remaining arguments. Default arguments are as for update_wrapper().
       This is a convenience function to simplify applying partial() to
       update_wrapper().

       Fixed on xoutil:

       Since most decorators use the *args, **kwargs idiom for arguments it is
       introduced the `add_signature` argument to prepend the signature to the
       documentation.
    """
    return partial(update_wrapper, wrapped=wrapped,
                   assigned=assigned, updated=updated,
                   add_signature=add_signature)

