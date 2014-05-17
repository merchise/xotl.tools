#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_annotations
#----------------------------------------------------------------------
# Copyright (c) 2012, 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on Apr 3, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)


import pytest

from xoutil.annotate import annotate
from xoutil.six import class_types


def test_keywords():
    @annotate(a=1, b={1: 4}, args=list, return_annotation=tuple)
    def dummy():
        pass

    assert dummy.__annotations__.get('a', None) == 1
    assert dummy.__annotations__.get('b', None) == {1: 4}
    assert dummy.__annotations__.get('args', None) == list
    assert dummy.__annotations__.get('return', None) == tuple


def test_signature():
    @annotate('(a: 1, b: {1: 4}, *args: list, **kwargs: dict) -> tuple')
    def dummy():
        pass

    assert dummy.__annotations__.get('a', None) == 1
    assert dummy.__annotations__.get('b', None) == {1: 4}
    assert dummy.__annotations__.get('args', None) == list
    assert dummy.__annotations__.get('return', None) == tuple
    assert dummy.__annotations__.get('kwargs', None) == dict
    assert dummy.__annotations__.get('return', None) == tuple


def test_invalid_nonsense_signature():
    with pytest.raises(SyntaxError):
        @annotate('(a, b) -> list')
        def dummy(a, b):
            pass

    # But the following is ok
    @annotate('() -> list')
    def dummy2(a, b):
        return 'Who cares about non-annotated args?'


def test_mixed_annotations():
    from xoutil.six import text_type

    @annotate('(a: str, b:text_type) -> bool', a=text_type,
              return_annotation=True)
    def dummy():
        pass

    assert dummy.__annotations__.get('a') is text_type
    assert dummy.__annotations__.get('b') is text_type
    assert dummy.__annotations__.get('return') is True


# It seems that playing with locals in frames in PyPy is not good-citizen
# behavior and some of these tests causes pytest to abort (not just fail).
@pytest.mark.skipif(str("sys.version.find('PyPy') != -1"))
def test_locals_vars():
    args = (1, 2)
    def ns():
        args = (3, 4)
        @annotate('(a: args)')
        def dummy():
            pass
        return dummy

    dummy = ns()
    assert dummy.__annotations__.get('a') == (3, 4)

    @annotate('(a: args)')
    def dummy():
        pass
    assert dummy.__annotations__.get('a') == (1, 2)


@pytest.mark.skipif(str("sys.version.find('PyPy') != -1"))
def test_globals():
    @annotate('(a: class_types)')
    def dummy():
        pass
    assert dummy.__annotations__['a'] == class_types


@pytest.mark.skipif(str("sys.version.find('PyPy') != -1"))
def test_closures_with_locals():
    '''
    Tests closures with locals variables.

    In Python 2.7 this behaves as we do (raises a NameError exception)::

        >>> def something():
        ...    args = 1
        ...    l = eval('lambda: args')
        ...    l()

        >>> something()
        Traceback (most recent call last):
            ...
        NameError: global name 'args' is not defined
    '''
    args = (1, 2)
    @annotate('(a: lambda: args)')
    def dummy():
        pass

    with pytest.raises(NameError):
        dummy.__annotations__.get('a', lambda: None)()
        assert False, 'It should have raised a NameError'
