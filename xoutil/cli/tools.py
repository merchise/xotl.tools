#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.cli.tools
#----------------------------------------------------------------------
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

__docstring_format__ = 'rst'
__author__ = 'med'


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

    '''
    from StringIO import StringIO
    buf = StringIO()
    start = True
    for letter in cls.__name__:
        if letter.isupper():
            if not start:
                buf.write(str('-'))
            letter = letter.lower()
        buf.write(letter)
        start = False
    buf.flush()
    res = buf.getvalue()
    buf.close()
    return res
