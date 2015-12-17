#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.cli
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 3 mai 2013

'''Define tools for command-line interface (CLI) applications.

CLi is a means of interaction with a computer program where the user (or
client) issues commands to the program in the form of successive lines of text
(command lines).

.. versionadded:: 1.4.1

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

from abc import abstractmethod, ABCMeta
from xoutil.eight.meta import metaclass
from xoutil.objects import classproperty
from .tools import command_name, program_name


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
                from xoutil.eight import typeof
                obj = 'Instance %s of class %s' % (id(instance),
                                                   typeof(instance).__name__)
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
            sub_commands.extend(getattr(source, '_abc_registry', ()))
            cmds = getattr(source, '__commands__', None)
            if cmds:
                sub_commands.extend(cmds())
            if sub_commands:
                for cmd in sub_commands:
                    self._settle_cache(cmd, recursed=recursed)
            else:   # Only branch commands are OK to execute
                self.cache[command_name(source)] = source
        else:
            raise ValueError('Reused class name "%s"!' % name)


class Command(metaclass(ABCMeta)):
    '''A command base registry.

    There are several methods to register new commands:

      * Inheriting from this class
      * Using the ABC mechanism of `register` virtual subclasses.
      * Registering a class with the method "__commands__" defined.

    If the method "__commands__" is used, it must be a class or static method.

    Command names are calculated as class names in lower case inserting a
    hyphen before each new capital letter. For example "MyCommand" will be
    used as "my-command".

    Each command could include its own argument parser, but it isn't used
    automatically, all arguments will be passed as a single parameter to
    :meth:`run` removing the command when obtained from "sys.argv".

    '''
    __default_command__ = None

    def __str__(self):
        return command_name(type(self))

    def __repr__(self):
        return '<command: %s>' % command_name(type(self))

    @classproperty
    def registry(cls):
        '''Obtain all registered commands.'''
        if cls is Command:
            name = '__registry__'
            res = getattr(cls, name, {})
            if not res:
                cls._settle_cache(res, Command)
                assert res.pop(command_name(Command), None) is None
                cls._check_help(res)
                setattr(cls, name, res)
            return res
        else:
            msg = ('Invalid class "%s" for use this property, only allowed in '
                   '"Command"!')
            raise TypeError(msg % cls.__name__)
        # = RegistryDescriptor()

    @abstractmethod
    def run(self, args=None):
        '''Must return a valid value for "sys.exit"'''
        if args is None:
            args = []
        raise NotImplementedError

    @classmethod
    def set_default_command(cls, cmd=None):
        '''A default command can be defined for call it when no one is
        specified.

        A command is detected when its name appears as the first command-line
        argument.

        To specify a default command, use this method with the command as a
        string (the command name) or the command class.

        If the command is specified, then the calling class is the selected
        one.

        For example::

            >>> Command.set_default_command('server')  # doctest: +SKIP
            >>> Server.set_default_command()           # doctest: +SKIP
            >>> Command.set_default_command(Server)    # doctest: +SKIP

        '''
        if cls is Command:
            if cmd is not None:
                from xoutil.eight import string_types as text
                name = cmd if isinstance(cmd, text) else command_name(cmd)
            else:
                raise ValueError('missing command specification!')
        else:
            if cmd is None:
                name = command_name(cls)
            else:
                msg = 'redundant command specification: "%s" and "%s"!'
                raise ValueError(msg % (cls, cmd))
        Command.__default_command__ = name

    @staticmethod
    def _settle_cache(target, source, recursed=None):
        '''`target` is a mapping to store result commands'''
        if recursed is None:
            recursed = set()
        # TODO: Convert check based in argument "recursed" in a decorator
        from xoutil.names import nameof
        name = nameof(source, inner=True, full=True)
        if name not in recursed:
            recursed.add(name)
            sub_commands = type.__subclasses__(source)
            sub_commands.extend(getattr(source, '_abc_registry', ()))
            cmds = getattr(source, '__commands__', None)
            if cmds:
                from collections import Iterable
                if not isinstance(cmds, Iterable):
                    cmds = cmds()
                sub_commands.extend(cmds)
            if sub_commands:
                for cmd in sub_commands:
                    Command._settle_cache(target, cmd, recursed=recursed)
            else:   # Only branch commands are OK to execute
                from types import MethodType
                assert isinstance(source.run, MethodType)
                target[command_name(source)] = source
        else:
            raise ValueError('Reused class "%s"!' % name)

    @staticmethod
    def _check_help(target):
        '''Check that correct help command is present.'''
        name = HELP_NAME
        hlp = target[name]
        if hlp is not Help and not getattr(hlp, '__overwrite__', False):
            target[name] = Help


class Help(Command):
    '''Show all commands

    Define the class attribute `__order__` to sort commands in special command
    "help".

    Commands could define its help in the first line of a sequence of
    documentations until found:

      - command class,
      - "run" method,
      - definition module.

    This command could not be overwritten unless using the class attribute:

       __override__ = True

    '''

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

    def run(self, args=[]):
        print('The most commonly used "%s" commands are:' % program_name())
        cmds = Command.registry
        ordered = [(getattr(cmds[cmd], '__order__', 0), cmd) for cmd in cmds]
        ordered.sort()
        max_len = len(max(ordered, key=lambda x: len(x[1]))[1])
        for _, cmd in ordered:
            cmd_class = cmds[cmd]
            doc = self._strip_doc(cmd_class.__doc__)
            if not doc:
                doc = self._strip_doc(cmd_class.run.__doc__)
            if not doc:
                import sys
                mod_name = cmd_class.__module__
                module = sys.modules.get(mod_name, None)
                if module:
                    doc = self._strip_doc(module.__doc__)
                    doc = '"%s"' % (doc if doc else mod_name)
                else:
                    doc = '"%s"' % mod_name
            head = ' '*3 + cmd + ' '*(2 + max_len - len(cmd))
            print(head, doc)

    @staticmethod
    def _strip_doc(doc):
        if doc:
            doc = str('%s' % doc).strip()
            return str(doc.strip().split('\n')[0].strip('''.'" \t\n\r'''))
        else:
            return ''


HELP_NAME = command_name(Help)

# TODO: Create "xoutil.config" here

del RegistryDescriptor
del abstractmethod, ABCMeta
del metaclass, classproperty
