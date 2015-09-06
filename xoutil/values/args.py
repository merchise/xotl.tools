#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.values.args
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-09-06

'''Simple function argument validator.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


def param_get(args, kwargs, idx, name, default=None):
    '''Get an argument value that could be given by order or by name.'''
    if idx < len(args):
        if name not in kwargs:
            return args[idx]
        else:
            msg = 'Argument repeated in order "{}" and with name ""'
            raise TypeError(msg.format(idx, name))
    else:
        return kwargs.get(name, default)
