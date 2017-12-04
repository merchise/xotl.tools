#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Tools for Command-Line Interface (CLI) applications.

CLI is a mean of interaction with a computer program where the user (or
client) issues commands to the program in the form of successive lines of text
(command lines).

Commands can be registered by:

  - sub-classing the `Command`:class:,
  - using `~abc.ABCMeta.register`:meth: ABC mechanism for virtual sub-classes,
  - redefining `~`Command.sub_commands`` class method.

.. versionadded:: 1.4.1

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.eight.abc import abstractmethod, ABC
from xoutil.objects import staticproperty
from xoutil.cli.tools import command_name, program_name


class Command(ABC):
    '''Base for all commands.

    '''
    __settings__ = {
        # 'default_command' : None
    }

    @classmethod
    def cli_name(cls):
        '''Calculate the command name.

        Standard method uses `~xoutil.cli.tools.hyphen_name`.  Redefine it
        to obtain a different behaviour.

        Example::

            >>> class MyCommand(Command):
            ...     pass

            >>> MyCommand.cli_name() == 'my-command'
            True

        '''
        from xoutil.eight import string_types
        from xoutil.cli.tools import hyphen_name
        unset = object()
        names = ('command_cli_name', '__command_name__')
        i, res = 0, unset
        while i < len(names) and res is unset:
            name = names[i]
            res = getattr(cls, names[i], unset)
            if res is unset:
                i += 1
            elif not isinstance(res, string_types):
                msg = "Attribute '{}' must be a string.".format(name)
                raise TypeError(msg)
        if res is unset:
            res = hyphen_name(cls.__name__)
        return res

    def __str__(self):
        return command_name(type(self))

    def __repr__(self):
        return '<command: %s>' % command_name(type(self))

    @staticproperty
    def registry():
        '''Obtain all registered commands.'''
        name = '__registry__'
        res = getattr(Command, name, {})
        if not res:
            Command._settle_cache(res, Command)
            assert res.pop(command_name(Command), None) is None
            Command._check_help(res)
            setattr(Command, name, res)
        return res

    @abstractmethod
    def run(self, args=None):
        '''Must return a valid value for "sys.exit"'''
        raise NotImplementedError

    @classmethod
    def get_setting(cls, name, *default):
        unset = object()
        aux = len(default)
        if aux == 0:
            default = unset
        elif aux == 1:
            default = default[0]
        else:
            msg = 'get_setting() takes at most 3 arguments ({} given)'
            raise TypeError(msg.format(aux + 2))
        res = cls.__settings__.get(name, default)
        if res is not unset:
            return res
        else:
            raise KeyError(name)

    @classmethod
    def set_setting(cls, name, value):
        cls.__settings__[name] = value    # TODO: Check type

    @classmethod
    def set_default_command(cls, cmd=None):
        '''Default command is called when no one is specified.

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
                # TODO: consider reset to None
                raise ValueError('missing command specification!')
        else:
            if cmd is None:
                name = command_name(cls)
            else:
                raise ValueError('redundant command specification', cls, cmd)

        Command.set_setting('default_command', name)

    @staticmethod
    def _settle_cache(target, source, recursed=None):
        '''`target` is a mapping to store result commands'''
        # TODO: Convert check based in argument "recursed" in a decorator
        import sys
        from xoutil.names import nameof
        if recursed is None:
            recursed = set()
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
                if sys.version_info < (3, 0):
                    from types import MethodType as ValidMethodType
                else:
                    from types import FunctionType as ValidMethodType
                assert isinstance(source.run, ValidMethodType), \
                    'Invalid type %r for source %r' % (
                        type(source.run).__name__,
                        source
                    )  # noqa
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
    '''Show all commands.

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
        # TODO: Use 'add_subparsers' in this logic (see 'backlog.org').
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
            head = ' ' * 3 + cmd + ' ' * (2 + max_len - len(cmd))
            print(head, doc)

    @staticmethod
    def _strip_doc(doc):
        if doc:
            doc = str('%s' % doc).strip()
            return str(doc.split('\n')[0].strip('''"' \t\n\r'''))
        else:
            return ''


HELP_NAME = command_name(Help)

# TODO: Create "xoutil.config" here

del abstractmethod, ABC
del staticproperty
