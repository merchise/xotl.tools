#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.cli.app
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on 7 mai 2013

'''An example of an application that use "xoutil.cli"

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

__docstring_format__ = 'rst'
__author__ = 'med'


def main(default=None):
    '''
    Execute a command, it can be given as the first program argument or it's
    the default command is defined.

    '''
    import sys
    from xoutil.cli import Command, HELP_NAME
    args = sys.argv[1:]
    if args and not args[0].startswith('-'):
        cmd_name = args[0]
        args = args[1:]
    else:
        cmd_name = Command.__default_command__ or default or HELP_NAME
    cmds = Command.registry
    cmd = cmds.get(cmd_name)
    if not cmd:
        print('Command "%s" not found!\n' % cmd_name)
        cmd = cmds.get(HELP_NAME)
        args = []
    sys.exit(cmd().run(args))


if __name__ == "__main__":
    main()
