#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xotl.default_dict
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
# Created on Jan 9, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

__docstring_format__ = 'rst'
__author__ = 'manu'

from collections import defaultdict as py_defaultdict


class defaultdict(py_defaultdict):
    '''
    A hack for defaultdict that passes the key and a copy of self as a plain
    dict (to avoid infinity recursion) to the callable.
    
    Examples::
        
        >>> from xotl.default_dict import defaultdict
        >>> d = defaultdict(lambda key, d: 'a')
        >>> d['abc']
        'a'
        
        >>> d['abc'] = 1
        >>> d['abc']
        1
        
    Since the second parameter is actually a dict-copy, you may (unwisely) to
    the following::
    
        >>> d = defaultdict(lambda k, d: d[k])
        >>> d['abc']
        Traceback (most recent call last):
            ...
        KeyError: 'abc'
        
        
    You may use this as a drop-in replacement for collections.defaultdict::
    
        # collections.defaultdict passes no arguments to the default_factory callable
        >>> d = defaultdict(lambda: 1) 
        >>> d['abc']
        1
    '''
    def __missing__(self, key):
        if self.default_factory is not None:
            try:
                return self.default_factory(key, dict(self))
            except TypeError:
                # This is the error when the arguments are not expected.
                return super(defaultdict, self).__missing__(key)
        else:
            raise KeyError(key)


