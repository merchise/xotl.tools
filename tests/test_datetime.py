#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_datetime
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-03-25

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)


def test_daterange():
    from xoutil.datetime import date
    from xoutil.datetime import daterange
    result = list(daterange(date(1978, 10, 21), 13, 2))
    assert result[0] == date(1978, 10, 21)
    assert result[-1] == date(1978, 11, 2)
    result = list(daterange(date(1978, 10, 21), -13, -2))
    assert result[0] == date(1978, 10, 21)
    assert result[-1] == date(1978, 10, 9)
