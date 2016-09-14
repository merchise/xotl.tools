#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.future.warnings
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-09-14

'''Future extensions to Python part of the warnings subsystem.

Add `check_future`:func: function to check if future module is being use
correctly.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from warnings import *    # noqa
from warnings import __all__

__all__ = list(__all__)


def check_future(name):
    '''Check future module for being used correctly.

    If not, yield a deprecation warning.

    :param name: module name to check.

    '''
    prefix = '.'.join(__name__.split('.')[:-1])
    if not name.startswith(prefix):
        new_name = '{}.{}'.format(prefix, name.split('.')[-1])
        warn(('"{}" is now deprecated and it will be removed. Use "{}" '
              'instead.').format(name, new_name), stacklevel=2)
