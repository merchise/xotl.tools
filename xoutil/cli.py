#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.command
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
# Created on 3 mai 2013

'''Define a base class in order to use several commands in a CLI application.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

from abc import abstractmethod

__docstring_format__ = 'rst'
__author__ = 'med'



class RegistryDescriptor(object):
    '''Define a mechanism to obtain all registered commands.'''

    __slots__ = [str('cache')]

    def __init__(self):
        self.cache = {}

    def __get__(self, instance, owner):
        if instance is None and owner is Command:
            if not self.cache:
                self._settle_cache(Command)
                assert self.cache.pop(Command.__name__.lower(), None) is None
            return self.cache
        else:
            if instance:
                obj = 'Instance %s of class %s' % (id(instance),
                                             type(instance).__name__)
            else:
                obj = 'Class %s' % owner.__name__
            msg = 'Only allowed in class "Command"; used invalidly from "%s"!'
            raise AttributeError(msg % obj)

    def _settle_cache(self, source):
        sub_commands = source.__subclasses__()
        if sub_commands:
            for cmd in sub_commands:
                self._settle_cache(cmd)
        else:   # Only branch commands are OK to execute
            self.cache[source.__name__.lower()] = source


class Command(object):
    '''
    A command base registry.

    First line of this documentation is intentionally leaved blank because that
    line is used as the description of commands.

    To include a new command, inherits from this class.

    Command names are calculated as class names in lower case inserting a
    hyphen before each new capital letter. For example "MyCommand" will be
    used as "my-command".

    Each command must include its own set of options definitions. To settle
    them, define a static or class method named "get_arg_parser" in your
    command class. See :class:`Help` for an example.

    Define the class attribute `__order__` to sort commands in help.

    '''
    registry = RegistryDescriptor()

    @abstractmethod
    def run(self):
        raise NotImplemented

    @classmethod
    def command_name(cls):
        '''Command names are calculated as class names in lower case inserting
        a hyphen before each new capital letter. For example "MyCommand" will
        be used as "my-command".

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

    @staticmethod
    def program_name():
        import sys
        from os.path import basename
        return basename(sys.argv[0])

    @classmethod
    def get_usage_prog(cls):
        '''Redefine this method to overwrite the way of usage assign
        program+command name to "prog" attribute.

        The default method is to concatenate the program base name in
        "sys.argv[0]" plus the command name.

        This is automa
        '''
        return '%s %s' % (cls.program_name(), cls.command_name())


class Help(Command):
    __order__ = -9999

    @classmethod
    def get_arg_parser(cls):
        '''This is an example on how to build local argument parser.

        Use class method "get

        '''
        res = getattr(cls, '_arg_parser')
        if not res:
            from argparse import ArgumentParser
            res = ArgumentParser()
            cls._arg_parser = res
        return res


del RegistryDescriptor, Help, abstractmethod
