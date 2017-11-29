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

from hypothesis import given, example
from hypothesis.strategies import text, binary


def test_slugify():
    from xoutil.string import slugify
    value = '  Á.e i  Ó  u  '
    assert slugify(value) == 'a-e-i-o-u'
    assert slugify(value, '.', invalid_chars='AU') == 'e.i.o'
    assert slugify(value, valid_chars='.') == 'a.e-i-o-u'
    assert slugify('_x', '_') == '_x'
    assert slugify('-x', '_') == 'x'
    assert slugify('-x-y-', '_') == 'x_y'
    assert slugify(None) == 'none'
    assert slugify(1 == 1) == 'true'
    assert slugify(1.0) == '1-0'
    assert slugify(135) == '135'
    assert slugify(123456, '', invalid_chars='52') == '1346'
    assert slugify('_x', '_') == '_x'


# FIXME: Dont filter; `slugify` should consider this.
valid_replacements = text().filter(lambda x: '\\' not in x)


@given(s=text(), invalid_chars=text(), replacement=valid_replacements)
@example(s='0/0', invalid_chars='-', replacement='-')
def test_slugify_hypothesis(s, invalid_chars, replacement):
    # TODO: (s='0:0', invalid_chars='z', replacement='ź')
    from xoutil.string import slugify
    from xoutil.eight.string import force_ascii

    assert ' ' not in slugify(s), 'Slugs do not contain spaces'

    assert ' ' in slugify(s + ' ', valid_chars=' '), \
        'Slugs do contain spaces if explicitly allowed'

    replacement = force_ascii(replacement).lower()
    invalid_chars = force_ascii(invalid_chars).lower()
    assert all(c not in slugify(s, replacement, invalid_chars=c)
               for c in invalid_chars if c not in replacement), \
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
