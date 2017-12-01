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


def test_csv():
    from xoutil.eight import text_type
    from xoutil.future.csv import parse, DefaultDialect

    data = ['A,B,C,D',
            '1,1.2,1.3,Spanish',
            '2,2.2,2.3,Español',
            '''"One, comma","""double quotes""",I'm a single quote,Inglés'''
    ]

    def forge(cell):
        try:
            return int(cell)
        except ValueError:
            try:
                return float(cell)
            except ValueError:
                return cell

    matrix = [[forge(cell) for cell in row] for row in parse(data)]

    sum_int, sum_float = 0, 0.0
    count_int, count_float, count_text = 0, 0, 0
    for row in matrix:
        for cell in row:
            if isinstance(cell, int):
                count_int += 1
                sum_int += cell
            elif isinstance(cell, float):
                count_float += 1
                sum_float += cell
            else:
                assert isinstance(cell, text_type)
                count_text += 1

    assert count_int == 2
    assert sum_int == 3
    assert sum_float == 7.0
    assert count_float == 4
    assert count_text == 10
