#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.uuid
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~] and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2012-02-17

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

__all__ = ['uuid']

from xoutil.deprecation import deprecated
from xoutil.cl.ids import str_uuid


@deprecated(str_uuid)
def uuid(random=False):
    '''Return a "Global Unique ID" as a string.

    :param random: If True, a random uuid is generated (does not use host id).

    '''
    return str_uuid(random)


del deprecated
