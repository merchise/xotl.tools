#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.aop.extended
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
# Created on Apr 29, 2012

'''
An extension to :py:mod:`xoutil.aop.classical` that allows to hook *before* and
*around* the :py:func:`~xoutil.aop.classical.weave` itself.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

__docstring_format__ = 'rst'
__author__ = 'manu'

__all__ = (b'weave', )


from xoutil.aop.classical import weave as classical_weave



def weave(aspect, target):
    '''
    Similar to :py:func:`xoutil.aop.classical.weave` but introduces
    _before_weave and _around_weave hooks to the weaving process::

        >>> class Foobar(object):
        ...    def echo(self, what):
        ...        return what

        >>> class FooAspect(object):
        ...    @classmethod
        ...    def _around_weave(self, method, aspect, target):
        ...        print('Weaving {who}'.format(who=target))
        ...        method(self._NestedAspect, target)
        ...
        ...    class _NestedAspect(object):
        ...        @classmethod
        ...        def _before_weave(self, target):
        ...            print('... with a nested!')
        ...
        ...        def after_echo(self, method, result, exc):
        ...            if not exc:
        ...                return result * 2

        >>> weave(FooAspect, Foobar)    # doctest: +ELLIPSIS
        Weaving <class '...Foobar'>
        ... with a nested!

        >>> f = Foobar()
        >>> f.echo(10)
        20

        >>> f.echo('a')
        'aa'
    '''
    before_weave = getattr(aspect, '_before_weave', None)
    if before_weave:
        before_weave(target)
    around_weave = getattr(aspect, '_around_weave', None)
    if around_weave:
        return around_weave(weave, aspect, target)
    else:
        return classical_weave(aspect, target)
