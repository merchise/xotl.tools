#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.counter
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-11-19

'''Creation order sequence generator.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.tasking.safe import SafeData

_CREATION_ORDER = SafeData([1])

del SafeData


def next_creation_order():
    '''Get next creation order in a sequence to the given instance.

    This allows multiple instances to be sorted in order of creation (the
    counter is thread-safe).

    '''
    with _CREATION_ORDER as counter:
        res = counter[0]
        counter[0] += 1
    return res
