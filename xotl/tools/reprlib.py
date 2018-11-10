# Back-ported from Python 3.2.
# Copyright (c) 2001-2012, 2014-2016, Python Software Foundation; All rights reserved.
# Retains the licence of the Python Software Foundation.
# flake8: noqa
"""Redo the builtin repr() (representation) but with limits on most sizes."""

from reprlib import Repr, repr, recursive_repr, __all__
