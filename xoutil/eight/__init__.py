#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2015-02-26

'''Xoutil extensions for writing code that runs on Python 2 and 3

The name comes from (Manu's idea') "2 raised to the power of 3".

There is an existing library written by "Benjamin Peterson" named `six`_, both
(`xoutil.eight` and `six`) can be used together since this module don't claim
to be a replacement of `six`, just some extra extensions.

This module also fixes some issues from PyPy interpreter.

.. _six: https://pypi.python.org/pypi/six

'''


import sys

# Python versions

_py2 = sys.version_info[0] == 2
_py3 = sys.version_info[0] == 3
_pypy = sys.version.find('PyPy') >= 0

del sys


try:
    intern = intern
except NameError:
    from sys import intern    # noqa
