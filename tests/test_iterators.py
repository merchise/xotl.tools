#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# tests.test_iterators
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-04-12

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from hypothesis import strategies as s, given, assume


def test_first_n_no_filling():
    from xoutil.iterators import first_n
    try:
        next(first_n((), 1))
        assert False, 'Should have raised an StopIteration'
    except StopIteration:
        pass
    except:
        assert False, 'Should have raised an StopIteration'


def test_first_n_filling_by_cycling():
    from xoutil.iterators import first_n
    assert list(first_n((), 10, range(5))) == [0, 1, 2, 3, 4] * 2


def test_first_n_repeat_filling_by_repeating():
    from xoutil.iterators import first_n
    from itertools import repeat
    assert list(first_n((), 10, '0')) == list(repeat('0', 10))


def test_first_n_simple():
    from xoutil.iterators import first_n
    assert list(first_n(range(100), 10, 0)) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_slides():
    from xoutil.iterators import slides
    assert list(slides(range(1, 11))) == [(1, 2),
                                          (3, 4),
                                          (5, 6),
                                          (7, 8),
                                          (9, 10)]


def test_slides_filling():
    from xoutil.iterators import slides
    assert list(slides(range(1, 5), 3)) == [(1, 2, 3), (4, None, None)]


def test_slides_with_repeating_filling():
    from xoutil.iterators import slides
    aux = [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, None, None)]
    assert list(slides(range(1, 11), width=3, fill=None)) == aux


def test_slides_with_cycling_filling():
    from xoutil.iterators import slides
    aux = [(1, 2, 3, 4, 5), (6, 7, 8, 9, 10), (11, 1, 2, 1, 2)]
    assert list(slides(range(1, 12), width=5, fill=(1, 2))) == aux


def test_continuously_slides():
    from xoutil.iterators import continuously_slides
    aux = continuously_slides('maupasant', 3, '')
    trigrams = list(''.join(x) for x in aux)
    assert 'mau' in trigrams
    assert 'aup' in trigrams
    assert 'upa' in trigrams
    assert 'pas' in trigrams
    assert 'asa' in trigrams
    assert 'san' in trigrams
    assert 'ant' in trigrams
    assert len(trigrams) == 7


@s.composite
def keys(draw):
    return 'k%d' % draw(s.integers(min_value=0, max_value=100))


@given(s.dictionaries(keys(), s.integers()),
       s.dictionaries(keys(), s.integers()))
def test_dict_update_new(d1, d2):
    from xoutil.iterators import dict_update_new
    d = dict(d1)
    dict_update_new(d1, d2)
    assert all(key in d1 for key in d2)
    assert all(d1[key] == d2[key] for key in d2 if key not in d)


@given(s.lists(s.integers()), s.integers(min_value=0))
def test_delete_duplicates(l, pos):
    from xoutil.iterators import delete_duplicates
    from xoutil.collections import Counter
    assume(0 <= pos < len(l))
    res = delete_duplicates(l)
    assert type(l) is type(res)  # noqa
    assert len(res) <= len(l)
    assert Counter(res)[l[pos]] == 1
