#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.aop
#----------------------------------------------------------------------
# Copyright (c) 2012 Medardo Rodríguez
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
# Created on Apr 26, 2012

'''
Very simple AOP implementation allowing method replacing in objects with change
function, reset an object to its original state and user a special super
function inner new functions used to inject the new behavior.

Aspect-oriented programming (AOP) increase modularity by allowing the separation
of cross-cutting concerns.

An aspect can alter the behavior of the base code (the non-aspect part of a
program) by applying advice (additional behavior) at various join-points (points
in a program) specified in a quantification or query called a point-cut (that
detects whether a given join point matches).

An aspect can also make structural changes to other classes, like adding members
or parents.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from .basic import complementor, inject_dependencies, weaved

__all__ = (b'complementor', 
           b'inject_dependencies', 
           b'weaved', )
