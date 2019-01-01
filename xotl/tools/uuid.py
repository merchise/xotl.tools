#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from xotl.tools.values.ids import str_uuid    # noqa

from xotl.tools.deprecation import deprecate_module
deprecate_module(replacement=str_uuid.__module__)
del deprecate_module


uuid = str_uuid    # noqa
