#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# tests.test_names
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on 16 avr. 2013


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


from xoutil.collections import OrderedSmartDict


def test_nameof():
    from xoutil.names import nameof
    from collections import OrderedDict as sorted_dict
    assert nameof(sorted_dict) == 'sorted_dict'
    assert nameof(sorted_dict, inner=True) == 'OrderedDict'
    sd = sorted_dict(x=1, y=2)
    assert nameof(sd) == 'sd'
    assert nameof(sd, typed=True) == 'sorted_dict'
    assert nameof(sd, inner=True, typed=True) == 'OrderedDict'
    s = 'foobar'
    assert nameof(s, inner=True) == 'foobar'
    # The following needs to be tested outside the assert, cause in Py3.3,
    # py.test rewrites the assert sentences and the local scope `nameof`
    # searched is not reached properly.
    passed = nameof('foobar') == 's'
    assert passed

    i = 1
    assert nameof(i) == 'i'
    assert nameof(i, inner=True) == '1'
    assert nameof(i, typed=True) == 'int'
    assert hex(id(sd)) in nameof(sd, inner=True)


def test_fullnameof():
    from xoutil.names import nameof
    from collections import OrderedDict as sorted_dict
    assert nameof(sorted_dict, full=True) == 'test_fullnameof.sorted_dict'
    assert nameof(sorted_dict, inner=True, full=True) == 'collections.OrderedDict'
    sd = sorted_dict(x=1, y=2)
    assert nameof(sd, full=True) == 'test_fullnameof.sd'
    assert nameof(sd, typed=True, full=True) == 'test_fullnameof.sorted_dict'
    assert nameof(sd, inner=True, typed=True, full=True) == 'collections.OrderedDict'


def test_fullnameof_no_rename():
    from xoutil.names import nameof
    from collections import OrderedDict
    assert nameof(OrderedDict, full=True) == 'test_fullnameof_no_rename.OrderedDict'
    assert nameof(OrderedDict, inner=True, full=True) == 'collections.OrderedDict'


def test_module_level_name():
    from xoutil.names import nameof
    assert nameof(OrderedSmartDict) == 'OrderedSmartDict'
    assert nameof(OrderedSmartDict, typed=True) == 'OrderedSmartDict'


def test_module_level_name_isolated():
    from xoutil.names import nameof
    assert nameof(OrderedSmartDict, full=True) == 'test_names.OrderedSmartDict'
