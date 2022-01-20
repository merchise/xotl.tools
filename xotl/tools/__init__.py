#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Collection of disparate utilities.

``xotl.tools`` is essentially an extension to the Python's standard library,
it does not make up a full framework, but it's very useful to be used from a
diversity of scenarios.

"""

from ._version import get_versions  # type: ignore

__version__ = get_versions()["version"]
del get_versions
