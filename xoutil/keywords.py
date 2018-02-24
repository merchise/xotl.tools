#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Tools for manage Python keywords as names.

Reserved Python keywords can't be used as attribute names, so this module
functions use the convention of rename the name using an underscore as
suffix when a reserved keyword is used as name.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

# TODO: Integrate -in one- this module with 'xoutil.eight.string' and rename
# it.


def suffix_kwd(name):
    '''Add an underscore suffix if name if a Python keyword.'''
    from keyword import iskeyword
    return '{}_'.format(name) if iskeyword(name) else name


def org_kwd(name):
    '''Remove the underscore suffix if name starts with a Python keyword.'''
    from keyword import iskeyword
    if name.endswith('_'):
        res = name[:-1]
        return res if iskeyword(res) else name
    else:
        return name


def getkwd(obj, name, default=None):
    '''Like `getattr` but taking into account Python keywords.'''
    return getattr(obj, suffix_kwd(name), default)


def setkwd(obj, name, value):
    '''Like `setattr` but taking into account Python keywords.'''
    setattr(obj, suffix_kwd(name), value)


def delkwd(obj, name):
    '''Like `delattr` but taking into account Python keywords.'''
    delattr(obj, suffix_kwd(name))


def kwd_getter(obj):
    '''partial(getkwd, obj)'''
    from functools import partial
    return partial(getkwd, obj)


def kwd_setter(obj):
    '''partial(setkwd, obj)'''
    from functools import partial
    return partial(setkwd, obj)


def kwd_deleter(obj):
    '''partial(delkwd, obj)'''
    from functools import partial
    return partial(delkwd, obj)
