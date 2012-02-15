#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# untitled.py
#----------------------------------------------------------------------
# Copyright (c) 2011 Merchise H8
# All rights reserved.
#
# Author: Manuel Vázquez Acosta <mva.led@gmail.com>
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
# Created on 2011-11-08

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

"Several util functions for iterators"

__docstring_format__ = 'rst'
__version__ = '0.1.0'
__author__ = 'Manuel Vázquez Acosta <mva.led@gmail.com>'

def first(pred, iterable, default=None):
    '''
    Returns the first element of an iterable that matches pred.

    Examples::

        >>> first(lambda x: x > 4, range(10))
        5

        >>> first(lambda x: x < 4, range(10))
        0

    If nothing matches the default is returned::

        >>> first(lambda x: x > 100, range(10), False)
        False
    '''
    from itertools import dropwhile
    try:
        return next(dropwhile(lambda x: not pred(x), iterable))
    except StopIteration:
        return default

def get_first(iterable):
    'Returns the first element of an iterable.'
    return first(lambda x: True, iterable)
