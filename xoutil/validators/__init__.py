# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.validators
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# Copyright (c) 2011, 2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created 2014-05-06

'''Some generic value validators and regular expressions and validation
functions for several identifiers.

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)


def is_type(cls):
    '''Return a validator with the same name as the type given as argument
    `value`.

    :param cls: Class or type or tuple of several types.

    '''
    def inner(obj):
        '''Check is a value object is a valid instance of (%s).'''
        return isinstance(obj, cls)

    if isinstance(cls, tuple):
        name = None
        for t in cls:
            if name:
                name += str('_or_%s' % t.__name__)
            else:
                name = t.__name__
    else:
        name = cls.__name__
    inner.__name__ = name
    inner.__doc__ = inner.__doc__ % name
    return inner
