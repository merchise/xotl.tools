#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.optparse
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
# Created 2012/12/27

'''Extensible 'argparse' module with some utilities.

  * function 'super_store' return an action closure that execute normal
    behavior of 'store' action and also execute other arguments actions with
    values passed as keyword arguments.

'''

from __future__ import (absolute_import as _py3_absolute,
                        division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)


__docstring_format__ = 'rst'
__author__ = 'med'
__version__ = '0.9.0'


def store_also(**kwargs):
    if kwargs:
        from argparse import _StoreAction

        class InnerAction(_StoreAction):
            def __call__(self, parser, namespace, values, option_string=None):
                super(InnerAction, self).__call__(parser, namespace, values,
                                                  option_string=option_string)
                for option in kwargs:
                    value = kwargs[option]
                    if len(option) == 1:
                        os = '-%s' % option
                    else:
                        os = '--%s' % option.replace('_', '-')
                    action = parser._option_string_actions.get(os)
                    if action:
                        action(parser, namespace, value, option_string=os)
                    else:
                        setattr(namespace, option, value)

        return InnerAction
    else:
        raise ValueError('At least one keyword argument must be provided')
