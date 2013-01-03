#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.optparse
#----------------------------------------------------------------------
# Copyright (c) 2012 Merchise Autrement
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
# Created 2012/12/27

'''
A powerful, extensible, and easy-to-use option parser.

Based in the Python's original by Greg Ward <gward@python.net>

See global 'optparse' help for more info.

Simple usage example::

   from xoutil.optparse import OptionParser

   parser = OptionParser()
   parser.add_option('-f', '--file', dest='filename', type='optional'
                     help='write report to FILE', metavar='FILE')
   parser.add_option('-q', '--quiet',
                     action='store_false', dest='verbose', default=True,
                     help="don't print status messages to stdout")

   (options, args) = parser.parse_args()

This is different from original in that you can use a new type for long options
('optional'). It's similar to strings, but allow you to use the plain option
or with an argument.

For example, both are valids:
    testapp --backup
    testapp --backup=~/temp
'''

from __future__ import (absolute_import as _py3_absolute,
                        division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)


__docstring_format__ = 'rst'
__author__ = 'med'
__version__ = '0.9.0'


import optparse as _pm

SUPPRESS_HELP = _pm.SUPPRESS_HELP
SUPPRESS_USAGE = _pm.SUPPRESS_USAGE
Values = _pm.Values
OptionContainer = _pm.OptionContainer
OptionGroup = _pm.OptionGroup
HelpFormatter = _pm.HelpFormatter
IndentedHelpFormatter = _pm.IndentedHelpFormatter
TitledHelpFormatter = _pm.TitledHelpFormatter
OptParseError = _pm.OptParseError
OptionError = _pm.OptionError
OptionConflictError = _pm.OptionConflictError
OptionValueError = _pm.OptionValueError
BadOptionError = _pm.BadOptionError

AmbiguousOptionError = _pm.AmbiguousOptionError
check_choice = _pm.check_choice
isbasestring = _pm.isbasestring
NO_DEFAULT = _pm.NO_DEFAULT
check_builtin = _pm.check_builtin

__all__ = getattr(_pm, '__all__', [])



class Option(_pm.Option, object):
    TYPES = _pm.Option.TYPES + ('optional',)


make_option = Option


class Values(_pm.Values, object):
    def __getattr__(self, name):
        return getattr(self.__dict__, name)


class OptionParser(_pm.OptionParser, object):
    def __init__(self, usage=None, option_list=None, option_class=Option,
                 version=None, conflict_handler='error', description=None,
                 formatter=None, add_help_option=True, prog=None,
                 epilog=None):
        super(OptionParser, self).__init__(usage=usage,
                                           option_list=option_list,
                                           option_class=option_class,
                                           version=version,
                                           conflict_handler=conflict_handler,
                                           description=description,
                                           formatter=formatter,
                                           add_help_option=add_help_option,
                                           prog=prog, epilog=epilog)

    def _process_long_opt(self, rargs, values):
        arg = rargs[0]
        if '=' in arg:
            opt, value = arg.split('=', 1)
        else:
            opt, value = arg, ''
        opt = self._match_long_opt(opt)
        option = self._long_opt[opt]
        if option.type == 'optional':
            rargs.pop(0)
            option.process(opt, value, values, self)
        else:
            super(OptionParser, self)._process_long_opt(rargs, values)

    def get_default_values(self):
        '''Patch to use new 'Values' class.'''
        if not self.process_default_values:
            return Values(self.defaults)
        else:
            defaults = self.defaults.copy()
            for option in self._get_all_options():
                default = defaults.get(option.dest)
                if isbasestring(default):
                    opt_str = option.get_opt_string()
                    defaults[option.dest] = option.check_value(opt_str, default)
            return Values(defaults)



# take out auxiliary module variable
del _pm
