#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.testbed
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# Copyright (c) 2012 Medardo Rodríguez
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

'''
This module simply serves the purposes of the testing weaving modules
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)


def echo(what):
    return what


from xoutil.modules import moduleproperty, modulemethod

@moduleproperty
def this(self):
    return self


def rien():
    return 1

@modulemethod
def method(self, *args, **kwargs):
    return self, args, kwargs


@modulemethod
def selfish(self):
    return self.selfish, selfish
