#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.cli.tools
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-05-05

'''Utilities for command-line interface (CLI) applications.

- `program_name`:func:\ : calculate the program name from "sys.argv[0]".

- `command_name`:func:\ : calculate command names using class names in lower
   case inserting a hyphen before each new capital letter.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


def program_name():
    '''Calculate the program name from "sys.argv[0]".'''
    # TODO: Use 'argparse' standard (parser.prog)
    import sys
    from os.path import basename
    return basename(sys.argv[0])


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
    from xoutil.eight import string_types
    from xoutil.future.string import hyphen_name
    unset = object()
    names = ('command_cli_name', '__command_name__')
    i, res = 0, unset
    while i < len(names) and res is unset:
        name = names[i]
        res = getattr(cls, names[i], unset)
        if res is unset:
            i += 1
        elif not isinstance(res, string_types):
            raise TypeError("Attribute '{}' must be a string.".format(name))
    if res is unset:
        res = hyphen_name(cls.__name__)
    return res
