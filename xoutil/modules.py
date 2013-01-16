#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.modules
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement
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
# Created on 13 janv. 2013

'''Module utilities.

It's common in `xoutil` package to extend Python modules with the same name,
for example `xoutil.datetime` has all public members of Python's `datetime`.
:func:`copy_members` can be used to copy all members from the original module
to the extended one.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


__docstring_format__ = 'rst'
__author__ = 'med'



def force_module(ref=None):
    '''Load a module from a string or return module if already created.

    If `ref` is not specified (or integer) calling module is assumed looking
    in the stack.

    .. impl-detail::

       Function used to inspect the stack is not guaranteed to exist in all
       implementations of Python.

    '''
    from types import ModuleType
    if isinstance(ref, ModuleType):
        return ref
    else:
        if ref is None:
            ref = 1
        if isinstance(ref, int):
            import sys
            ref = sys._getframe(ref).f_globals['__name__']
        if not isinstance(ref, str):
            if isinstance(ref, bytes):
                ref = ref.decode()  # Python 3.x
            else:
                try:
                    ref = ref.encode()  # Python 2.x
                except:
                    msg = ("invalid type '%s' for module name '%s'" %
                            (type(ref), ref))
                    raise TypeError(msg)
        return __import__(ref, fromlist=[ref], level=0)


def copy_members(source=None, target=None):
    '''Copy module members from `source` to `target`.

    :param source: string with source module name or module itself.

        If not given, is assumed as the last module part name of `target`.

    :param target: string with target module name or module itself.

        If not given, target name is looked in the stack of caller module.

    :returns: Source module.
    :rtype: `ModuleType`

    .. impl-detail::

       Function used to inspect the stack is not guaranteed to exist in all
       implementations of Python.

    '''
    target = force_module(target or 2)
    if source is None:
        source = target.__name__.rsplit('.')[-1]
        if source == target.__name__:
            msg = '"source" and "target" modules must be different.'
            raise ValueError(msg)
    source = force_module(source)
    for attr in dir(source):
        if not attr.startswith('__'):
            setattr(target, attr, getattr(source, attr))
    return source
