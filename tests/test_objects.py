#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# tests.test_objects
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-04-16

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

import pytest
from xoutil.objects import smart_copy

__author__ = "Manuel Vázquez Acosta <mva.led@gmail.com>"
__date__   = "Tue Apr 16 10:22:16 2013"


def test_smart_copy():
    class new(object):
        def __init__(self, **kw):
            for k, v in kw.items():
                setattr(self, k, v)

    source = new(a=1, b=2, c=4, _d=5)
    target = {}
    smart_copy(source, target, False)
    assert target == dict(a=1, b=2, c=4)

    target = {}
    smart_copy(source, target, True)
    assert target['_d'] == 5


def test_smart_copy_with_defaults():
    defaults = {'host': 'localhost', 'port': 5432, 'user': 'openerp',
                'password': (KeyError, '{key}')}
    kwargs = {'password': 'keep-out!'}
    args = smart_copy(kwargs, {}, defaults=defaults)
    assert args == dict(host='localhost', port=5432, user='openerp', password='keep-out!')

    # if missing a required key
    with pytest.raises(KeyError):
        args = smart_copy({}, {}, defaults=defaults)
