#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.tasking
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-10-25

'''Multitasking and concurrent programming tools.

.. warning:: Experimental.  API is not settled.

.. versionadded:: 1.8.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import sys

# TODO: Must be implemented using `xoutil.api` mechanisms for correct driver
# determination, in this case "thread-local data".
if 'greenlet' in sys.modules:
    from ._greenlet_local import local    # noqa
else:
    try:
        from threading import local    # noqa
    except ImportError:
        from dummy_threading import local    # noqa

del sys


class AutoLocal(local):
    '''Initialize thread-safe local data in one shoot.

    Typical use is::

        >>> from xoutil.tasking import AutoLocal
        >>> context = AutoLocal(cause=None, traceback=None)

    When at least one attribute is given, ``del AutoLocal`` it's executed
    automatically avoiding this common statement at the end of your module.

    '''
    def __init__(self, **attrs):
        import sys
        super(AutoLocal, self).__init__()
        for attr in attrs:
            setattr(self, attr, attrs[attr])
        if attrs:
            g = sys._getframe(1).f_globals
            tname = type(self).__name__
            if tname in g:
                del g[tname]
