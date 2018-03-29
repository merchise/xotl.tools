#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Special logical values like Unset, Undefined, Ignored, Invalid, ...

All values only could be `True` or `False` but are intended in places where
`None` is expected to be a valid value or for special Boolean formats.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)


SYMBOL = 'symbol'
BOOLEAN = 'boolean'

TIMEOUT = 2.0


class MetaSymbol(type):
    '''Meta-class for symbol types.'''
    def __new__(cls, name, bases, ns):
        if ns['__module__'] == __name__ or name not in {SYMBOL, BOOLEAN}:
            self = super().__new__(cls, name, bases, ns)
            if name == SYMBOL:
                self._instances = {str(v): v for v in (False, True)}
            return self
        else:
            raise TypeError('invalid class "{}" declared outside of "{}" '
                            'module'.format(name, __name__))

    def __instancecheck__(self, instance):
        '''Override for isinstance(instance, self).'''
        if instance is False or instance is True:
            return True
        else:
            return super().__instancecheck__(instance)

    def __subclasscheck__(self, subclass):
        '''Override for issubclass(subclass, self).'''
        if subclass is bool:
            return True
        else:
            return super().__subclasscheck__(subclass)

    def nameof(self, s):
        '''Get the name of a symbol instance (`s`).'''
        from xoutil.eight import iteritems
        items = iteritems(self._instances)
        return next((name for name, value in items if value is s), None)

    def parse(self, name):
        '''Returns instance from a string.

        Standard Python Boolean values are parsed too.

        '''
        from xoutil.eight import type_name
        if '#' in name:    # Remove comment
            name = name.split('#')[0].strip()
        res = self._instances.get(name, None)
        if res is not None:
            if isinstance(res, self):
                return res
            else:
                msg = 'invalid parsed value "{}" of type "{}"; must be "{}"'
                rtn, sn = type_name(res), self.__name__
                raise TypeError(msg.format(res, rtn, sn))
        else:
            msg = 'name "{}" is not defined'
            raise NameError(msg.format(name))


class symbol(int, metaclass=MetaSymbol):
    '''Instances are custom symbols.

    Symbol instances identify uniquely a semantic concept by its name.  Each
    one has an ordinal value associated.

    For example::

      >>> ONE2MANY = symbol('ONE2MANY')
      >>> ONE_TO_MANY = symbol('ONE2MANY')

      >>> ONE_TO_MANY is ONE2MANY
      True

    '''
    __slots__ = ()

    def __new__(cls, name, value=None):
        '''Get or create a new symbol instance.

        :param name: String representing the internal name.  `Symbol`:class:
               instances are unique (singletons) in the context of this
               argument.  ``#`` and spaces are invalid characters to allow
               comments.

        :param value: Any value compatible with Python `bool` or `int` types.
               `None` is used as a special value to create a value using the
               name hash.

        '''
        from xoutil.eight import intern as unique, type_name
        name = unique(name)
        if name:
            if value is None:
                value = hash(name)
            res = cls._instances.get(name)
            if res is None:    # Create the new instance
                if isinstance(value, int):
                    res = super().__new__(cls, value)
                    cls._instances[name] = res
                else:
                    msg = ('instancing "{}" with name "{}" and incorrect '
                           'value "{}" of type "{}"')
                    cn, vt = cls.__name__, type_name(value)
                    raise TypeError(msg.format(cn, name, value, vt))
            elif res != value:    # Check existing instance
                msg = 'value "{}" mismatch for existing instance: "{}"'
                raise ValueError(msg.format(value, name))
            return res
        else:
            raise ValueError('name must be a valid non empty string')

    def __init__(self, *args, **kwds):
        pass

    def __repr__(self):
        return symbol.nameof(self)

    __str__ = __repr__


class boolean(symbol):
    '''Instances are custom logical values (`True` or `False`).

    Special symbols allowing only logical (False or True) values.

    For example::

      >>> true = boolean('true', True)
      >>> false = boolean('false')
      >>> none = boolean('false')
      >>> unset = boolean('unset')

      >>> class X:
      ...      attr = None

      >>> getattr(X(), 'attr') is not None
      False

      >>> getattr(X(), 'attr', false) is not false
      True

      >>> none is false
      True

      >>> false == False
      True

      >>> false == unset
      True

      >>> false is unset
      False

      >>> true == True
      True

    '''
    __slots__ = ()

    def __new__(cls, name, value=False):
        '''Get or create a new symbol instance.

        See `~Symbol.__new__`:meth: for information about parameters.
        '''
        return super().__new__(cls, name, bool(value))


# --- Special singleton values ---

#: False value, mainly for function parameter definitions, where None could
#: be a valid value.
Unset = boolean('Unset')

#: False value for local scope use or where ``Unset`` could be a valid value
Undefined = boolean('Undefined')

#: To be used in arguments that are currently ignored because they are being
#: deprecated.  The only valid reason to use `Ignored` is to signal ignored
#: arguments in method's/function's signature
Ignored = boolean('Ignored')

#: To be used in functions resulting in a fail where False could be a valid
#: value.
Invalid = boolean('Invalid')

#: To be used as a mark for current context as a mechanism of comfort.
This = boolean('This', True)
