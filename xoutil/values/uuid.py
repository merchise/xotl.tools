#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.uuid
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
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
# Created on 2015-08-25

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)


def uuid(random=False):
    '''Return a "Global Unique ID" as a string.

    :param random: If True, a random uuid is generated (does not use host id).

    '''
    from uuid import uuid1, uuid4
    return '%s' % (uuid4 if random else uuid1)()
