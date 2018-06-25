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


def test_throw_catch():
    def get_sample():
        import sys
        from xoutil.eight.exceptions import throw, catch
        res = []
        try:
            try:
                1/0
            except catch(Exception) as error:
                res.append(error)
                traceback = sys.exc_info()[2]
                res.append(traceback)
                # replace for:
                # raise RuntimeError().with_traceback(traceback) from error
                throw(RuntimeError(), traceback=traceback, cause=error)
        except catch(Exception) as error:
            res.append(error)
            res.append(sys.exc_info()[2])
        return res

    data =  get_sample()
    assert data[2].__context__ is data[0]
    assert data[2].__cause__ is data[0]
    assert data[2].__traceback__ is data[3]
    assert data[0].__context__ is None
    assert data[0].__cause__ is None
    assert data[0].__traceback__ is data[1]
