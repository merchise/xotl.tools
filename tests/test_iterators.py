#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# tests.test_iterators
#----------------------------------------------------------------------
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
    assert list(slides(range(1, 11), width=3, fill=None)) == [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, None, None)]

def test_slides_with_cycling_filling():
    from xoutil.iterators import slides
    assert list(slides(range(1, 12), width=5, fill=(1, 2))) == [(1, 2, 3, 4, 5), (6, 7, 8, 9, 10), (11, 1, 2, 1, 2)]


def test_continuously_slides():
    from xoutil.iterators import continuously_slides
    trigrams = list(''.join(x) for x in continuously_slides('maupasant', 3, ''))
    assert 'mau' in trigrams
    assert 'aup' in trigrams
    assert 'upa' in trigrams
    assert 'pas' in trigrams
    assert 'asa' in trigrams
    assert 'san' in trigrams
    assert 'ant' in trigrams
    assert len(trigrams) == 7
