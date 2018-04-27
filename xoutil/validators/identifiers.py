#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''
Regular expressions and validation functions for several identifiers.
'''

from re import compile as _regex_compile
from xoutil.eight import string_types


__all__ = ('is_valid_identifier', 'is_valid_full_identifier',
           'is_valid_public_identifier',
           'is_valid_slug')


def is_valid_identifier(name):
    '''Returns True if `name` a valid Python identifier.

    If `name` is not a string, return False.  This is roughly::

        isinstance(name, str) and name.isidentifier()

    '''
    return isinstance(name, str) and name.isidentifier()


def check_identifier(name):
    '''Checks if `name` a valid Python identifier.

    If not, an exception is raised.

    '''
    if is_valid_identifier(name):
        return name
    else:
        raise ValueError('"%s" is not a valid identifier!' % name)


def is_valid_full_identifier(name):
    '''Returns True if `name` is a valid dotted Python identifier.

    See `is_valid_identifier`:func: for what "validity" means.

    '''
    if isinstance(name, str):
        return all(part.isidentifier() for part in name.split('.'))
    else:
        return False


def is_valid_public_identifier(name):
    '''Returns True if `name` is a valid Python identifier that is deemed
    public.

    Convention says that any name starting with a "_" is not public.

    See `is_valid_identifier`:func: for what "validity" means.

    '''
    return is_valid_identifier(name) and not name.startswith('_')


_SLUG_REGEX = _regex_compile('(?i)^[\w]+([-][\w]+)*$')


def is_valid_slug(slug):
    return isinstance(slug, string_types) and _SLUG_REGEX.match(slug)
