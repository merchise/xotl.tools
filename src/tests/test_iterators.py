#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from hypothesis import given
from hypothesis import strategies as s


def test_slides():
    from xotl.tools.future.itertools import slides

    assert list(slides(range(1, 11))) == [
        (1, 2),
        (3, 4),
        (5, 6),
        (7, 8),
        (9, 10),
    ]


def test_slides_with_repeating_filling():
    from xotl.tools.future.itertools import NO_FILL, slides

    assert list(slides(range(1, 11), width=3, fill=None)) == [
        (1, 2, 3),
        (4, 5, 6),
        (7, 8, 9),
        (10, None, None),
    ]
    assert list(slides(range(1, 11), width=3, fill=NO_FILL)) == [
        (1, 2, 3),
        (4, 5, 6),
        (7, 8, 9),
        (10,),
    ]


def test_slides_with_cycling_filling():
    from xotl.tools.future.itertools import slides

    assert list(slides(range(1, 12), width=5, fill=(1, 2, 3))) == [
        (1, 2, 3, 4, 5),
        (6, 7, 8, 9, 10),
        (11, 1, 2, 3, 1),
    ]


def test_continuously_slides():
    from xotl.tools.future.itertools import continuously_slides

    aux = continuously_slides("maupasant", 3, "")
    trigrams = list("".join(x) for x in aux)
    assert "mau" in trigrams
    assert "aup" in trigrams
    assert "upa" in trigrams
    assert "pas" in trigrams
    assert "asa" in trigrams
    assert "san" in trigrams
    assert "ant" in trigrams
    assert len(trigrams) == 7


@s.composite
def keys(draw):
    return "k%d" % draw(s.integers(min_value=0, max_value=100))


@given(s.dictionaries(keys(), s.integers()), s.dictionaries(keys(), s.integers()))
def test_dict_update_new(d1, d2):
    from xotl.tools.future.itertools import dict_update_new

    d = dict(d1)
    dict_update_new(d1, d2)
    assert all(key in d1 for key in d2)
    assert all(d1[key] == d2[key] for key in d2 if key not in d)


@given(s.lists(s.integers(), max_size=30))
def test_delete_duplicates(ls):
    from collections import Counter

    from xotl.tools.future.itertools import delete_duplicates

    res = delete_duplicates(ls)
    assert type(ls) is type(res)  # noqa
    assert len(res) <= len(ls)
    assert all(Counter(res)[item] == 1 for item in ls)


@given(s.lists(s.integers(), max_size=30))
def test_delete_duplicates_with_key(ls):
    from xotl.tools.future.itertools import delete_duplicates

    res = delete_duplicates(ls, key=lambda x: x % 3)
    assert len(res) <= 3, "key yields 0, 1, or 2; thus res can contain at most 3 items"


def test_iter_delete_duplicates():
    from xotl.tools.future.itertools import iter_delete_duplicates

    assert list(iter_delete_duplicates("AAAaBBBA")) == ["A", "a", "B", "A"]
    assert list(iter_delete_duplicates("AAAaBBBA", key=lambda x: x.lower())) == [
        "A",
        "B",
        "A",
    ]

    assert list(iter_delete_duplicates("AAAaBBBA")) == ["A", "a", "B", "A"]
    assert list(iter_delete_duplicates("AAAaBBBA", key=lambda x: x.lower())) == ["A", "B", "A"]
