#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.aop
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
# Created on Mar 23, 2012

'''
Very simple AOP implementation allowing method replacing in objects with push
function, recover the last state with pop, reset an object to its original state
and user a special super function inner new functions used to inject the new
behavior.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

__docstring_format__ = 'rst'
__author__ = 'Medardo Rodriguez'


from xoutil.types import Unset


# Following attribute name is used to store method queues inner objects.
_ATTR_REPLACED_METHODS = '::replaced-methods'



def push_method(obj, name, new_function):
    '''
    Inject the new function as replacement of existing method.
    '''
    replaced_methods = getattr(obj, _ATTR_REPLACED_METHODS, Unset)
    if replaced_methods is Unset:
        replaced_methods = {}
        setattr(obj, _ATTR_REPLACED_METHODS, replaced_methods)
    queue = replaced_methods.setdefault(name, [])
    queue.append(getattr(obj, name, None))
    setattr(obj, name, new_function)


def pop_method(obj, name):
    '''
    Pop a method from the queue and restore the previous state.
    '''
    replaced_methods = getattr(obj, _ATTR_REPLACED_METHODS, Unset)
    if replaced_methods is not Unset:
        queue = replaced_methods.get(name, Unset)
        if queue is not Unset:
            last = queue.pop()
            if len(queue) == 0:
                del replaced_methods[name]
            if last is not None:
                aux = getattr(last, 'im_class', Unset)
                if aux != type(obj):
                    setattr(obj, name, last)
                else:
                    delattr(obj, name)
            else:
                delattr(obj, name)
        else:
            raise ValueError('No "%s" injected method in this object!' % name)
    else:
        raise ValueError("This object hasn't injected methods!")


def super_method(obj, name):
    '''
    Return the previous method in the queue or None.
    '''
    replaced_methods = getattr(obj, _ATTR_REPLACED_METHODS, Unset)
    if replaced_methods is not Unset:
        queue = replaced_methods.get(name, Unset)
        if queue is not Unset:
            from traceback import extract_stack
            ss = extract_stack(limit=2)[-2]
            print(':::::::', ss)
            i = len(queue) - 1
            found = None
            while (found is None) and (i > 0):
                m = queue[i]
                if (m.__name__ == ss[2]) and (m.func_code.co_filename == ss[0]):
                    found = queue[i - 1]
                    print('======== FOUND')
                else:
                    i -= 1
            return found if found is not None else queue[-1]
        else:
            return None
    else:
        return None
