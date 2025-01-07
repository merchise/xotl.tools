#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#


def test_ppformat_rtype():
    from xotl.tools.future.pprint import ppformat

    o = [list(range(i + 1)) for i in range(10)]
    assert type(ppformat(o)) is str
