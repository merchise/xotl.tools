#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.config
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
# Created on 2013/01/04

'''Integrate `ConfigParser` and `argparse` using the simple function
:func:`get_options`.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

__docstring_format__ = 'rst'
__author__ = 'med'



def get_config(program=None, config_path=None, **defaults):
    '''Reads the `program` configuration options by traversing all folders in
    `config_path` looking for configuration files and updating options to be
    returned in each step.

    :param program: The logical name of the program. If not given, is
                    smartly calculated from `sys.argv[0]`. It's used by
                    trying the suffixes ``('', 'rc', '.cfg', '.config')`` in
                    each step. If the folder to try is ``'~'``, then the prefix
                    ``'.'`` is appended and only the first two suffixes are
                    used.

    :param config_path: Folders to iteratively find configuration files.

                        If a `str` is given, then is split using `os.pathsep`.

                        If a 'list` is given, each element should be either a
                        folder name or a tuple of mutually exclusive folder
                        names.

                        If `None` (the default) is given, then the following is
                        used::

                          ['/etc', ('~/.config', '~'), os.path.dirname(sys.argv[0]), '.']

    :type config_path: `str` or a `list` of strings.

    :param defaults: A set of initial default options.

    :returns: The set of all options concatenated in all steps.
              pattern at the end.
    :rtype: `dict`

    '''


def get_options(parser, program=None, config_path=None, **defaults):
    '''After read configuration files using :func:`get_config`, update
    obtained options with the argument `parser`.

    :param parser: An argument parser full definition.
    :type parser: argparse.ArgumentParser

    :param ...: See :func:`get_config` for the meaning of other parameters.

    :returns: Full options concatenating those in configuration files and
              updated with current arguments.
    :rtype: argparse.Namespace

    '''
    # from ConfigParser import ConfigParser as _
