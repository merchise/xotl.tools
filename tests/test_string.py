#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_string
#----------------------------------------------------------------------
# Copyright (c) 2015, 2016 Merchise and Contributors
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

from hypothesis import given
from hypothesis.strategies import text, binary


@given(s=binary())
def test_safe_decode_dont_fail_uppon_invalid_encoding(s):
    from xoutil.string import safe_decode
    assert safe_decode(s, 'i-dont-exist') == safe_decode(s)


@given(s=text())
def test_safe_encode_dont_fail_uppon_invalid_encoding(s):
    from xoutil.string import safe_encode
    assert safe_encode(s, 'i-dont-exist') == safe_encode(s)


def test_safe_string():
    from xoutil.string import safe_str
    from xoutil.eight import _py2
    aux = lambda x: 2*x + 1
    name = 'λ x: 2*x + 1'
    aux.__name__ = safe_str(name)
    delta = 1 if _py2 else 0
    assert len(aux.__name__) == len(name) + delta


def test_normalize_slug():
    from xoutil.string import normalize_slug
    assert normalize_slug('  Á.e i  Ó  u  ') == 'a-e-i-o-u'
    assert normalize_slug('  Á.e i  Ó  u  ', '.', invalids='AU') == 'e.i.o'
    assert normalize_slug('  Á.e i  Ó  u  ', valids='.') == 'a.e-i-o-u'
    assert normalize_slug('_x', '_') == '_x'
    assert normalize_slug('-x', '_') == 'x'
    assert normalize_slug('-x-y-', '_') == 'x_y'
    assert normalize_slug(None) == 'none'
    assert normalize_slug(1 == 1) == 'true'
    assert normalize_slug(1.0) == '1-0'
    assert normalize_slug(135) == '135'
    assert normalize_slug(123456, '', invalids='52') == '1346'
    assert normalize_slug('_x', '_') == '_x'


@given(s=text(), invalids=text())
def test_normalize_slug_hypothesis(s, invalids):
    from xoutil.string import normalize_slug

    assert ' ' not in normalize_slug(s), \
        'Slugs do not contain spaces'

    assert ' ' in normalize_slug(s + ' ', valids=' '), \
        'Slugs do contain spaces if explicitly allowed'

    # TODO: @med, The following fails with s='0' and invalids='0'.  Is this a
    # true invariant?
    assert all(c not in normalize_slug(s) for c in invalids), \
        'Slugs dont contain invalid chars'


@given(s=text(), p=text())
def test_cutting_is_inverse_to_adding(s, p):
    from xoutil.string import cut_prefix, cut_suffix
    assert cut_prefix(p + s, p) == s
    assert cut_suffix(s + p, p) == s
    assert cut_suffix(s, '') == s
    assert cut_prefix(s, '') == s


@given(s=text(), p=text())
def test_cutting_is_stable(s, p):
    from xoutil.string import cut_prefix, cut_suffix
    if not s.startswith(p):
        assert cut_prefix(s, p) == s == cut_prefix(cut_prefix(s, p), p)
    if not s.endswith(p):
        assert cut_suffix(s, p) == s == cut_suffix(cut_suffix(s, p), p)
