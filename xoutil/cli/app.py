#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''A simple `main`:func: entry point for CLI based applications.

This module provides an example of how to use `xoutil.cli`:mod: to create a
CLI application.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


def main(default=None):
    '''Execute a command.

    It can be given as the first program argument or it's the `default`
    command is defined.

    '''
    import sys
    from xoutil.cli import Command, HELP_NAME
    args = sys.argv[1:]
    if args and not args[0].startswith('-'):
        cmd_name = args[0]
        args = args[1:]
    else:
        cmd_name = (default or Command.get_setting('default_command', None) or
                    HELP_NAME)
    cmds = Command.registry
    cmd = cmds.get(cmd_name)
    if not cmd:
        print('Command "%s" not found!\n' % cmd_name)
        cmd = cmds.get(HELP_NAME)
        args = []
    sys.exit(cmd().run(args))


if __name__ == "__main__":
    main()
