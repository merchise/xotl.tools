#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.cli.app
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 7 mai 2013

'''A simple :func:`main` entry point for CLI based applications.

This module provides an example of how to use :mod:`xoutil.cli` to create a CLI
application.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


def main(default=None):
    '''Execute a command, it can be given as the first program argument or it's
    the default command is defined.

    '''
    import sys
    from xoutil.cli import Command, HELP_NAME
    args = sys.argv[1:]
    if args and not args[0].startswith('-'):
        cmd_name = args[0]
        args = args[1:]
    else:
        cmd_name = default or Command.__default_command__ or HELP_NAME
    cmds = Command.registry
    cmd = cmds.get(cmd_name)
    if not cmd:
        print('Command "%s" not found!\n' % cmd_name)
        cmd = cmds.get(HELP_NAME)
        args = []
    sys.exit(cmd().run(args))


if __name__ == "__main__":
    main()
