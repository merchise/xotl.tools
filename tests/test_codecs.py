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

from hypothesis import given
from hypothesis.strategies import text, binary


@given(s=binary())
def test_safe_decode_dont_fail_uppon_invalid_encoding(s):
    from xoutil.future.codecs import safe_decode
    assert safe_decode(s, 'i-dont-exist') == safe_decode(s)


@given(s=text())
def test_safe_encode_dont_fail_uppon_invalid_encoding(s):
    from xoutil.future.codecs import safe_encode
    assert safe_encode(s, 'i-dont-exist') == safe_encode(s)


@given(text())
def test_safe_encode_yields_bytes(s):
    from xoutil.future.codecs import safe_encode
    assert isinstance(safe_encode(s), bytes)


@given(binary())
def test_safe_decode_yields_unicode(s):
    try:
        Text = unicode
    except NameError:
        Text = str  # Python 3
    from xoutil.future.codecs import safe_decode
    assert isinstance(safe_decode(s), Text)
