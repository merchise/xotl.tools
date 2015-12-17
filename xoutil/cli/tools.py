#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.cli.tools
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 5 mai 2013

'''Utilities for command-line interface (CLI) applications.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


def program_name():
    '''Calculate the program name from "sys.argv[0]".'''
    import sys
    from os.path import basename
    return basename(sys.argv[0])


def command_name(cls):
    '''Command names are calculated as class names in lower case inserting a
    hyphen before each new capital letter. For example "MyCommand" will be
    used as "my-command".

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
    Unset = object()
    res = getattr(cls, 'command_cli_name', Unset)
    if res is not Unset:
        from xoutil.eight import string_types
        if not isinstance(res, string_types):
            raise TypeError("Attribute 'command_cli_name' must be a string.")
    else:
        from io import StringIO
        from xoutil.string import safe_decode
        buf = StringIO()
        start = True
        for letter in cls.__name__:
            if letter.isupper():
                if not start:
                    buf.write(safe_decode('-'))
                letter = letter.lower()
            buf.write(safe_decode(letter))
            start = False
        buf.flush()
        res = buf.getvalue()
        buf.close()
    return res
