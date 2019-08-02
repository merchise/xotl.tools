#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""Extensions to Python's `time` module.

You may use it as drop-in replacement of `time`.  Although we don't
document all items here.  Refer to `time`:mod: documentation.

.. note:: This module is deprecated since `monotonic` is included in
Python 3.3.

"""

from time import *  # noqa
from time import monotonic
import time as _stdlib  # noqa

from xotl.tools.deprecation import deprecate_module

deprecate_module(replacement=monotonic.__module__)
del deprecate_module
