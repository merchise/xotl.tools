#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.opendict
#----------------------------------------------------------------------
# Copyright (c) 2011 Merchise Autrement
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
# Created on Dec 13, 2011

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

__docstring_format__ = 'rst'
__author__ = 'manu'


class opendict(dict):
    '''
    A dictionary implementation that mirrors its keys as attributes::

        >>> d = opendict({'es': 'spanish'})
        >>> d.es
        'spanish'

        >>> d['es'] = 'espanol'
        >>> d.es
        'espanol'
        
    '''
    def __getattr__(self, name):
        try:
            return super(opendict, self).__getattr__(name)
        except AttributeError:
            if name in self:
                return self[name]
            else:
                raise
