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

from hypothesis import given, example
from hypothesis.strategies import text, binary


def test_force_string():
    from xoutil.eight import string
    # from xoutil.eight import python_version
    aux = lambda x: 2*x + 1
    name = 'λ x: 2*x + 1'
    aux.__name__ = string.force(name)
    delta = 0    # 1 if python_version == 2 else 0
    # TODO: Because future unicode_literals was removed.  Maybe this test must
    # be removed or reformulated.
    assert len(aux.__name__) == len(name) + delta
