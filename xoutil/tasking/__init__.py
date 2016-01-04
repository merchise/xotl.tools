#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.tasking
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-10-25

'''Multitasking and concurrent programming tools.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


# TODO: Next must be implemented using `xoutil.api` mechanisms for fixing
# correct driver for a concept, in this case "thread-local data".
import sys

if 'greenlet' in sys.modules:
    from ._greenlet_local import local    # noqa
else:
    try:
        from threading import local    # noqa
    except ImportError:
        from dummy_threading import local    # noqa

del sys
