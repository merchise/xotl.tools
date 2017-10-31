#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)

from xoutil.values.ids import str_uuid    # noqa

from xoutil.deprecation import deprecate_module
deprecate_module(replacement=str_uuid.__module__)
del deprecate_module


uuid = str_uuid    # noqa
