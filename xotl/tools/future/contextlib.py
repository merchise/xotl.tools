#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Python Software Foundation
# All rights reserved.
#
# Most of the contents of this file were extracted from the source code of
# CPython 3.6.
#

"""Utilities for `with-statement contexts <343>`:pep:.

This module re-export all symbols from the standard library, with the
exception of the function `nested`.

.. versionadded:: 1.9.5

"""

import contextlib as _stdlib  # noqa
from contextlib import *  # noqa

__all__ = list(getattr(_stdlib, "__all__", []))
