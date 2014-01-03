#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil._meta2
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-04-29

'''Implements the metaclass() function using the Py3k syntax.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from xoutil.compat import py3k
assert not py3k, 'This module should not be loaded in Py3k'

__author__ = "Manuel Vázquez Acosta <mva.led@gmail.com>"
__date__ = "Mon Apr 29 15:34:11 2013"


METACLASS_ATTR = str('__metaclass__')


def metaclass(meta):
    class base(object):
        pass

    class inner_meta(meta.__base__):
        def __new__(cls, name, bases, attrs):
            if name != '__inner__':
                bases = tuple(b for b in bases if not issubclass(b, base))
                if not bases:
                    bases = (object,)
                if METACLASS_ATTR in attrs:
                    attrs[METACLASS_ATTR] = meta
                return meta(name, bases, attrs)
            else:
                return type.__new__(cls, name, bases, attrs)


    class __inner__(base):
        __metaclass__ = inner_meta

    return __inner__
