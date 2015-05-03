#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.tools
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# Copyright (c) 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created 2014-05-15

'''Simple tools with no dependencies on other modules.

Extensions to the Python's standard library.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)


def get_default(args, default=None):
    '''Get a default value passed as last positional argument.

    Several functions that get values define an optional default value
    parameter.  To use a construction ``def get_foobar(name, default=None)``
    sometimes is not possible because `None` could be a possible valid
    "foobar" value.  In these cases it's better to construct something like::

      def get_foobar(name, *default):
          ...

    and in client code you can call this function with a impossible "foobar"
    value, like: ``res = get_foobar('egg', Undefined)`` (see `xoutil.values`).

    This function receive the tuple as received by the function, and which
    value to return if None is given::

      def get_foobar(name, *default):
          from xoutil.tools import get_default
          from xoutil import Undefined as _undef
          default = get_default(default, _undef)
          ...

    If tuple `args` has an invalid size, a `TypeError` exception is raised.

    '''
    count = len(args)
    if count == 0:
        return default
    elif count == 1:
        return args[0]
    else:
        raise TypeError("expected 0 or 1 values for default, got %s" % count)
