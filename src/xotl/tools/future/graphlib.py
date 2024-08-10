#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Backport of Python 3.9's grahlib module.

.. versionadded:: 2.1.9

.. deprecated:: 3.2.1

"""

from graphlib import CycleError, TopologicalSorter

__all__ = ["TopologicalSorter", "CycleError"]
