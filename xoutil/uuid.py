#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.uuid
# ---------------------------------------------------------------------
# Copyright (c) 2015, 2017 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Feb 17, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

from xoutil.names import strlist as strs
__all__ = strs('uuid', )
del strs

from xoutil.deprecation import deprecated
from xoutil.values.ids import str_uuid


@deprecated(str_uuid)
def uuid(random=False):
    '''Return a "Global Unique ID" as a string.

    :param random: If True, a random uuid is generated (does not use host id).

    '''
    return str_uuid(random)


del deprecated
