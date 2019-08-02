#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""Extend standard modules including "future" features in current versions.

Version 3 introduce several concepts in standard modules.  Sometimes these
features are implemented in the evolution of 2.7.x versions.  By using
sub-modules, these differences can be avoided transparently.  For example, you
can import `xotl.tools.future.collections.UserDict`:class: in any version,
that it's equivalent to Python 3 `collections.UserDict`:class:, but it don't
exists in Python 2.

.. versionadded:: 1.7.2

"""
