#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.tests.test_tools
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-10-07

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

def test_nameof():
    from xoutil.tools import nameof

    class foobar:
        pass

    singletons = (None, True, False, Ellipsis, NotImplemented)

    assert nameof(foobar) == nameof(foobar()) == 'foobar'
    assert nameof(object) == 'object'
    assert nameof(test_nameof) == 'test_nameof'

    assert nameof(lambda x: x) == '<lambda>'

    assert [nameof(s) for s in singletons] == ['None', 'True', 'False',
                                               'Ellipsis', 'NotImplemented']

    assert nameof(1) == 'int'
    assert nameof(1.0) == 'float'


# TODO: Add test for remainder functions in this module.
