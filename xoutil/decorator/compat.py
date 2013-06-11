#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.decorator.compat
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-01-15

'''Provides decorators related with interoperability Python 2 and Python 3.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from xoutil.deprecation import deprecated

from xoutil.names import strlist as strs
__all__ = strs('metaclass')
del strs

__author__ = "Manuel Vázquez Acosta <mva.led@gmail.com>"
__date__ = "Tue Jan 15 11:38:55 2013"


@deprecated('xoutil.objects.metaclass', removed_in_version='1.4.2',
            check_version=True)
def metaclass(meta):
    '''Declares a meta class transparently in Python 2 and Python 3.

    Example::

        >>> class Metaclass(type):
        ...     pass

        >>> @metaclass(Metaclass)
        ... class Something(object):
        ...    pass

        >>> type(Something)    # doctest: +ELLIPSIS
        <class '...Metaclass'>

    '''
    from xoutil.objects import copy_class
    return lambda cls: copy_class(cls, meta=meta)


def test_metaclass_decorator_with_slots():
    from xoutil.types import MemberDescriptorType

    class Meta(type):
        pass

    @metaclass(Meta)
    class Base(object):
        __slots__ = 'attr'

    @metaclass(Meta)
    class Ok(object):
        def __init__(self, **kwargs):
            self.__dict__ = kwargs


        @classmethod
        def clmethod(cls):
            return cls

        @staticmethod
        def stmethod(echo):
            return echo

        def echo(self, echo):
            return self, echo

    assert isinstance(Base.attr, MemberDescriptorType)
    assert isinstance(Base, Meta)
    assert isinstance(Ok, Meta)

    b = Base()
    b.attr = 1
    try:
        b.another = 2
        assert False, 'Should have raised AttributeError'
    except AttributeError:
        pass
    except:
        assert False, 'Should have raised AttributeError'

    ok = Ok(name='ok')
    assert ok.stmethod(ok) == ok
    assert ok.clmethod() == Ok
    assert ok.echo(1) == (ok, 1)
    assert ok.name == 'ok'
