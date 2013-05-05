#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.cli
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

'''Define tools for command-line interface (CLI) applications.

CLi is a means of interaction with a computer program where the user (or
client) issues commands to the program in the form of successive lines of text
(command lines).

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

from abc import abstractmethod, ABCMeta
from xoutil.objects import metaclass

__docstring_format__ = 'rst'
__author__ = 'med'



class RegistryDescriptor(object):
    '''Define a mechanism to automatically obtain all registered commands.'''

    __slots__ = [str('cache')]

    def __init__(self):
        self.cache = {}

    def __get__(self, instance, owner):
        if instance is None and owner is Command:
            if not self.cache:
                self._settle_cache(Command)
                assert self.cache.pop(command_name(Command), None) is None
            return self.cache
        else:
            if instance:
                obj = 'Instance %s of class %s' % (id(instance),
                                             type(instance).__name__)
            else:
                obj = 'Class %s' % owner.__name__
            msg = 'Only allowed in class "Command"; used invalidly from "%s"!'
            raise AttributeError(msg % obj)

    def _settle_cache(self, source, recursed=set()):
        # TODO: Convert check based in argument "recursed" in a decorator
        name = source.__name__
        if name not in recursed:
            recursed.add(name)
            sub_commands = source.__subclasses__()
            sub_commands.extend(source._abc_registry)
            if sub_commands:
                for cmd in sub_commands:
                    self._settle_cache(cmd, recursed=recursed)
            else:   # Only branch commands are OK to execute
                self.cache[command_name(source)] = source
        else:
            raise ValueError('Reused class name "%s"!' % name)


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


class Command(metaclass(ABCMeta)):
    '''A command base registry.

    There are several methods to register new commands:

      * Inherits from this class
      * Using the ABC mechanism of `register` virtual subclasses.
      * Redefining the class method "__subclasses__" of a registered class.
      * Modifying directly the registry.

    Command names are calculated as class names in lower case inserting a
    hyphen before each new capital letter. For example "MyCommand" will be
    used as "my-command".

    Each command could include its own argument parser, but it isn't used
    automatically, all arguments will be passed as a single parameter to
    :method:`run` removing the command when obtained from "sys.argv".
    Nevertheless, if the command define one class method named
    "get_arg_parser", then it will be used to complement the help of this
    command. See :method:`get_help` for more info.

    Define the class attribute `__order__` to sort commands in special command
    "help".

    '''
    registry = RegistryDescriptor()

    @abstractmethod
    def run(self, args=[]):
        raise NotImplemented

    @classmethod
    def get_help(cls):
        pass


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


del RegistryDescriptor, Help
del abstractmethod, ABCMeta
del metaclass
