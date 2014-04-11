#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_types
#----------------------------------------------------------------------
# Copyright (c) 2012, 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-11-25

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

__docstring_format__ = 'rst'
__author__ = 'manu'


def test_NoneType_exists():
    from xoutil.types import NoneType
    assert NoneType is type(None)


def test_iscollection():
    from xoutil.types import is_collection
    from xoutil.six.moves import range
    from xoutil.collections import UserList, UserDict
    assert is_collection('all strings are iterable') is False
    assert is_collection(1) is False
    assert is_collection(range(1)) is True
    assert is_collection({}) is False
    assert is_collection(tuple()) is True
    assert is_collection(set()) is True
    assert is_collection(a for a in range(100)) is True

    class Foobar(UserList):
        pass

    assert is_collection(Foobar()) is True

    class Foobar(UserDict):
        pass

    assert is_collection(Foobar()) is False
