#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)


import pytest
from xoutil.eight.abc import ABC
from xoutil.versions import python_version

skip_ver = python_version == 3 or python_version.pypy

@pytest.mark.skipif(skip_ver, reason='My WTF about this not working.')
def test_abc_base():
    class MyError(ABC, Exception):
        pass

    d, x = {}, 0

    try:
        x = d['x']
        assert False, 'Never executed.'
    except MyError:
        assert False, 'Never executed.'
    except Exception:
        x = 1
        assert True, 'Executed, but OK.'

    assert x == 1
    assert MyError.adopt(KeyError) == KeyError

    try:
        x = d['x']
        assert False, 'Never executed.'
    except MyError:
        x = 2
        assert True, 'Executed, but OK.'
    except Exception:
        assert False, 'Never executed.'

    assert x == 2


@pytest.mark.skipif(skip_ver, reason='My WTF about this not working.')
def test_abc_register():
    class MyError(Exception, ABC):
        pass

    @MyError.adopt
    class MyNewError(Exception):
        pass

    x = 0
    try:
        raise MyNewError('Test registered exception.')
        x = 1
    except MyError:
        x = 2
        assert True, 'Executed, but OK.'
    except Exception:
        x = 3
        assert False, 'Never executed.'

    assert x == 2
