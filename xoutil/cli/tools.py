#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.cli.tools
# ---------------------------------------------------------------------
# Copyright (c) 2015, 2016 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 5 mai 2013

'''Utilities for command-line interface (CLI) applications.

- `program_name`:func:\ : calculate the program name from "sys.argv[0]".

- `command_name`:fucn:\ : calculate command names using class names in lower
   case inserting a hyphen before each new capital letter.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


def program_name():
    '''Calculate the program name from "sys.argv[0]".'''
    import sys
    from os.path import basename
    return basename(sys.argv[0])


def hyphenize_name(name):
    '''Convert an identifier to a valid command name using hyphens.'''
    # XXX: In Python 3, identifiers could contain any unicode alphanumeric.
    import re
    res = name
    trans = tuple(re.finditer('[A-Z][a-z]', res))
    i = len(trans) - 1
    while i >= 0:
        m = trans[i]
        s = m.start()
        if s > 0:
            res = res[:s] + '-' + res[s:]
        i -= 1
    trans = tuple(re.finditer('[a-z][A-Z]', res))
    i = len(trans) - 1
    while i >= 0:
        m = trans[i]
        s = m.start() + 1
        res = res[:s] + '-' + res[s:]
        i -= 1
    return res.lower()


def command_name(cls):
    '''Calculate a command name from given class.

    Names are calculated putting class names in lower case and inserting
    hyphens before each new capital letter.  For example "MyCommand" will
    generate "my-command".

    It's defined as an external function because a class method don't apply to
    minimal commands (those with only the "run" method).

    Example::

        >>> class SomeCommand(object):
        ...     pass

        >>> command_name(SomeCommand) == 'some-command'
        True

    If the command class has an attribute `command_cli_name`, this will be
    used instead::

        >>> class SomeCommand(object):
        ...    command_cli_name = 'adduser'

        >>> command_name(SomeCommand) == 'adduser'
        True

    It's an error to have a non-string `command_cli_name` attribute::

        >>> class SomeCommand(object):
        ...    command_cli_name = None

        >>> command_name(SomeCommand)  # doctest: +ELLIPSIS
        Traceback (most recent call last):
           ...
        TypeError: Attribute 'command_cli_name' must be a string.

    '''
    unset = object()
    res = getattr(cls, 'command_cli_name', unset)
    if res is not unset:
        from xoutil.eight import string_types
        if isinstance(res, string_types):
            return res
        else:
            raise TypeError("Attribute 'command_cli_name' must be a string.")
    else:
        return hyphenize_name(cls.__name__)
