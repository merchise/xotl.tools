# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.future
#----------------------------------------------------------------------
# Copyright (c) 2011 Merchise Autrement
# All rights reserved.
#
# Author: Medardo Rodriguez
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# Created on Nov 11, 2011

'''
Definitions that will be used to declare structures that must be fixed.
'''


from __future__ import (division as _py3_division, print_function as _py3_print, unicode_literals as _py3_unicode)

import types as _types



class FutureModule(_types.ModuleType):
    '''
    Create a module from a class definition with this one as meta-class.
    Intended to create classes that will be migrated to modules in some future time.

    For example:
        >>> class decorators:
        ...     __metaclass__ = FutureModule
        ...     isnode = aliases(ancestor=b'parent', descendants=b'children')
        >>> @decorators.isnode
        ... class Foobar(object):
        ...     parent = b'The parent'
        ...     children = [1, 2, 3]
        >>> f = Foobar()
        >>> f.ancestor
        'The parent'
        >>> f.descendants
        [1, 2, 3]
    '''
    def __init__(self, name, args, kwargs):
        super(FutureModule, self).__init__(name, kwargs.pop('__doc__', None))
        copy_attrs(kwargs, self)



