#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.future._past
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-09-14

'''This is not a future extension module.

Add a function to assure that future module is being use correctly.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


def check(name=None):
    '''Check future module for being used correctly.

    If not, issue a deprecation warning.

    :param name: name of module to check (could be ``None`` to inspect it in
           the stack-frame).

    '''
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        try:
            name = frame.f_globals.get('__name__')
        finally:
            # As recommended in Python's documentation to avoid memory leaks
            del frame
    prefix = '.'.join(__name__.split('.')[:-1])
    if name and prefix not in name:
        from warnings import warn
        new_name = '{}.{}'.format(prefix, name.split('.')[-1])
        warn(('"{}" is now deprecated and it will be removed; use "{}" '
              'instead.').format(name, new_name),
             # TODO: Why ``category=DeprecationWarning,`` doesn't work?
             stacklevel=2)
