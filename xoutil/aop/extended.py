#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.aop.extended
#----------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# Copyright (c) 2012 Medardo Rodriguez
# All rights reserved.
#
# Author: Manuel Vázquez Acosta
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Apr 29, 2012

'''An extension to :mod:`xoutil.aop.classical` that allows to hook *before* and
*around* the :func:`~xoutil.aop.classical.weave` itself.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

from xoutil.aop.classical import weave as classical_weave
from xoutil.deprecation import deprecated as _deprecated
from xoutil.names import strlist as strs

__all__ = strs('weave')
del strs


@_deprecated('None', msg="This entire module is deprecated and will be "
             "removed.", removed_in_version='1.6.0')
def weave(aspect, target):
    '''Similar to :func:`xoutil.aop.classical.weave` but introduces
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
        ...        def _after_echo(self, method, result, exc):
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
        return classical_weave(aspect, target,
                               '_before_weave', '_around_weave')


del _deprecated
