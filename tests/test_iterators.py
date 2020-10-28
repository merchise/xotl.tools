#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import pytest
from hypothesis import strategies as s, given


def test_first_n_no_filling():
    from xotl.tools.future.itertools import first_n

    with pytest.raises(StopIteration):
        next(first_n((), 1))


def test_first_n_filling_by_cycling():
    from xotl.tools.future.itertools import first_n

    assert list(first_n((), 10, range(5))) == [0, 1, 2, 3, 4] * 2


def test_first_n_repeat_filling_by_repeating():
    from xotl.tools.future.itertools import first_n
    from itertools import repeat

    assert list(first_n((), 10, "0")) == list(repeat("0", 10))


def test_first_n_simple():
    from xotl.tools.future.itertools import first_n

    assert list(first_n(range(100), 10, 0)) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_slides():
    from xotl.tools.future.itertools import slides

    assert list(slides(range(1, 11))) == [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]


def test_slides_filling():
    from xotl.tools.future.itertools import slides

    assert list(slides(range(1, 5), 3)) == [(1, 2, 3), (4, None, None)]


def test_slides_with_repeating_filling():
    from xotl.tools.future.itertools import slides

    aux = [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, None, None)]
    assert list(slides(range(1, 11), width=3, fill=None)) == aux


def test_slides_with_cycling_filling():
    from xotl.tools.future.itertools import slides

    aux = [(1, 2, 3, 4, 5), (6, 7, 8, 9, 10), (11, 1, 2, 1, 2)]
    assert list(slides(range(1, 12), width=5, fill=(1, 2))) == aux


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
def test_delete_duplicates(l):
    from xotl.tools.future.itertools import delete_duplicates
    from xotl.tools.future.collections import Counter

    res = delete_duplicates(l)
    assert type(l) is type(res)  # noqa
    assert len(res) <= len(l)
    assert all(Counter(res)[item] == 1 for item in l)


@given(s.lists(s.integers(), max_size=30))
def test_delete_duplicates_with_key(l):
    from xotl.tools.future.itertools import delete_duplicates

    res = delete_duplicates(l, key=lambda x: x % 3)
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
    assert list(iter_delete_duplicates("AAAaBBBA", key=lambda x: x.lower())) == [
        "A",
        "B",
        "A",
    ]


@given(
    s.lists(s.integers(), max_size=30),
    s.lists(s.integers(), max_size=30),
    s.lists(s.integers(), max_size=30),
)
def test_merge(l1, l2, l3):
    from xotl.tools.future.itertools import merge

    l1 = sorted(l1)
    l2 = sorted(l2)
    l3 = sorted(l3)
    # Accumulate and catch if yielding more than necessary
    iter_ = merge(l1, l2, l3)
    expected = sorted(l1 + l2 + l3)
    result = []
    for _ in range(len(expected)):
        result.append(next(iter_))
    with pytest.raises(StopIteration):
        last = next(iter_)  # noqa: There cannot be more items in the merge
    assert result == expected


@given(s.lists(s.integers(), max_size=30), s.lists(s.integers(), max_size=30))
def test_merge_by_key(l1, l2):
    from xotl.tools.future.itertools import merge

    l1 = [("l1-dummy", i) for i in sorted(l1)]
    l2 = [("l2-dummy", i) for i in sorted(l2)]
    # Accumulate and catch if yielding more than necessary
    iter_ = merge(l1, l2, key=lambda x: x[1])
    expected = sorted(l1 + l2, key=lambda x: x[1])
    result = []
    for _ in range(len(expected)):
        result.append(next(iter_))
    with pytest.raises(StopIteration):
        last = next(iter_)  # noqa: There cannot be more items in the merge
    assert result == expected


@given(s.lists(s.integers(), max_size=30), s.lists(s.integers(), max_size=30))
def test_merge_by_key_incomparable(l1, l2):
    class item:
        def __init__(self, x):
            self.item = x

    from xotl.tools.future.itertools import merge

    l1 = [item(i) for i in sorted(l1)]
    l2 = [item(i) for i in sorted(l2)]
    # Accumulate and catch if yielding more than necessary
    iter_ = merge(l1, l2, key=lambda x: x.item)
    expected = sorted(l1 + l2, key=lambda x: x.item)
    result = []
    for _ in range(len(expected)):
        result.append(next(iter_))
    with pytest.raises(StopIteration):
        last = next(iter_)  # noqa: There cannot be more items in the merge
    assert result == expected
