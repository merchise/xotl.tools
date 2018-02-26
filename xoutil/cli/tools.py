#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Utilities for command-line interface (CLI) applications.

- `program_name`:func:\ : calculate the program name from "sys.argv[0]".

- `command_name`:func:\ : calculate command names using class names in lower
   case inserting a hyphen before each new capital letter.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


def hyphen_name(name, join_numbers=True):
    '''Convert a name to a hyphened slug.

    Expects a `name` in Camel-Case.  All invalid characters (those invalid in
    Python identifiers) are ignored.  Numbers are joined with preceding part
    when `join_numbers` is True.

    For example::

      >>> hyphen_name('BaseNode') == 'base-node'
      True

      >> hyphen_name('--__ICQNámeP12_34Abc--') == 'icq-name-p12-34-abc'
      True

      >> hyphen_name('ICQNámeP12', join_numbers=False) == 'icq-name-p-12'
      True

    '''
    import re
    from xoutil.eight.string import force_ascii
    name = force_ascii(name)
    regex = re.compile('[^A-Za-z0-9]+')
    name = regex.sub('-', name)
    regex = re.compile('([A-Z]+|[a-z]+|[0-9]+|-)')
    all = regex.findall(name)
    i, count, parts = 0, len(all), []
    while i < count:
        part = all[i]
        if part != '-':
            upper = 'A' <= part <= 'Z'
            if upper:
                part = part.lower()
            j = i + 1
            if j < count and upper and 'a' <= all[j] <= 'z':
                aux = part[:-1]
                if aux:
                    parts.append(aux)
                part = part[-1] + all[j]
                i = j
                j += 1
            if j < count and '0' <= all[j] <= '9' and join_numbers:
                part = part + all[j]
                i = j
            parts.append(part)
        i += 1
    return '-'.join(parts)


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

        >>> class SomeCommand:
        ...     pass

        >>> command_name(SomeCommand) == 'some-command'
        True

    If the command class has an attribute `command_cli_name`, this will be
    used instead::

        >>> class SomeCommand:
        ...    command_cli_name = 'adduser'

        >>> command_name(SomeCommand) == 'adduser'
        True

    It's an error to have a non-string `command_cli_name` attribute::

        >>> class SomeCommand:
        ...    command_cli_name = None

        >>> command_name(SomeCommand)  # doctest: +ELLIPSIS
        Traceback (most recent call last):
           ...
        TypeError: Attribute 'command_cli_name' must be a string.

    '''
    from xoutil.eight import string_types
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
