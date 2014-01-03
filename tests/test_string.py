#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_string
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-01-16

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

import pytest

@pytest.mark.skipif()
def test_normal_safe_formatter():
    from xoutil.string import SafeFormatter, safe_encode

    f = SafeFormatter(x=1, y=2)
    result = f.format(safe_encode('CWD: "{cwd}"; "x+d["x"]": {x+d["x"]}.'),
                      cwd=safe_encode('~/tmp/foóbar'), d=dict(x=1))
    assert 'CWD: "~/tmp/foóbar"; "x+d["x"]": 2.' == result
