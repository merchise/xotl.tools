#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from hypothesis import given, example
from hypothesis.strategies import text


def test_slugify():
    from xotl.tools.string import slugify

    value = "  Á.e i  Ó  u  "
    options = dict(encoding="utf-8")
    assert slugify(value, **options) == "a-e-i-o-u"
    assert slugify(value, ".", invalid_chars="AU", **options) == "e.i.o"
    assert slugify(value, valid_chars=".", **options) == "a.e-i-o-u"
    assert slugify("_x", "_") == "_x"
    assert slugify("-x", "_") == "x"
    assert slugify("-x-y-", "_") == "x_y"
    assert slugify(None) == "none"
    assert slugify(1 == 1) == "true"
    assert slugify(1.0) == "1-0"
    assert slugify(135) == "135"
    assert slugify(123456, "", invalid_chars="52") == "1346"
    assert slugify("_x", "_") == "_x"


# FIXME: Dont filter; `slugify` should consider this.
valid_replacements = text().filter(lambda x: "\\" not in x)


@given(s=text(), invalid_chars=text(), replacement=valid_replacements)
@example(s="0/0", invalid_chars="-", replacement="-")
def test_slugify_hypothesis(s, invalid_chars, replacement):
    # TODO: (s='0:0', invalid_chars='z', replacement='ź')
    from xotl.tools.string import slugify
    from xotl.tools.string import force_ascii

    assert " " not in slugify(s), "Slugs do not contain spaces"

    assert " " in slugify(
        s + " ", valid_chars=" "
    ), "Slugs do contain spaces if explicitly allowed"

    replacement = force_ascii(replacement).lower()
    invalid_chars = force_ascii(invalid_chars).lower()
    assert all(
        c not in slugify(s, replacement, invalid_chars=c)
        for c in invalid_chars
        if c not in replacement
    ), "Slugs dont contain invalid chars"


@given(s=text(), p=text())
def test_cutting_is_inverse_to_adding(s, p):
    from xotl.tools.string import cut_prefix, cut_suffix

    assert cut_prefix(p + s, p) == s
    assert cut_suffix(s + p, p) == s
    assert cut_suffix(s, "") == s
    assert cut_prefix(s, "") == s


@given(s=text(), p=text())
def test_cutting_is_stable(s, p):
    from xotl.tools.string import cut_prefix, cut_suffix

    if not s.startswith(p):
        assert cut_prefix(s, p) == s == cut_prefix(cut_prefix(s, p), p)
    if not s.endswith(p):
        assert cut_suffix(s, p) == s == cut_suffix(cut_suffix(s, p), p)
