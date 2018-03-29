#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#


'''Smart formatting.

.. deprecated:: 1.8.3  Use `~xoutil.future.collections.codedict`:class:.

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

from xoutil.eight import string_types as _str_base
from xoutil.deprecation import deprecate_module


deprecate_module('xoutil.future.collections.codedict')


class DelimiterFactory:
    def __new__(cls, owner, key, start, end):
        return key


class BaseFactory:
    _unsafe = False

    def __init__(self, owner, key, start, end):
        self.key = key
        self.match = owner.template[start:end]
        self.start = start


class MapFactory(BaseFactory):
    def __call__(self, mapping):
        from xoutil.eight import text_type
        return text_type(mapping[self.key])


class PyFactory(BaseFactory):
    def __init__(self, owner, key, start, end):
        super().__init__(owner, compile(key, '', 'eval'), start, end)

    def __call__(self, mapping):
        from xoutil.eight import text_type
        return text_type(eval(self.key, mapping))


class InvalidFactory:
    _unsafe = True

    def __init__(self, owner, key, start, end):
        self.owner = owner
        self.match = owner.template[start:end]
        self.start = start

    def __call__(self, mapping):
        start = self.start
        lines = self.owner.template[:start].splitlines(True)
        if lines:
            col = start - len(''.join(lines[:-1]))
            line = len(lines)
        else:
            col = line = 1
        msg = ('Invalid place-holder in string: '
               'line "%d", col "%d"') % (line, col)
        raise ValueError(msg)


class _TemplateClass(type):
    'Metaclass for Template.'

    # TODO: Not needed, convert to a static method

    _alters = (('escaped', r'(?P=delimiter)', '%s', DelimiterFactory),
               ('key', r'(?:[a-z_]\d*)+', '%s', MapFactory),
               ('xkey', r'[^?{}][^{}]*', '{%s}', MapFactory),
               ('python', r'[^{}]+', '{\?%s}', PyFactory),
               ('invalid', r'.', '%s', InvalidFactory))

    def __init__(cls, name, bases, attrs):
        import re
        super().__init__(name, bases, attrs)
        alters, factories = [], {}
        for kind, pattern, wrapper, factory in cls._alters:
            factories[kind] = factory
            alters.append(wrapper % ('(?P<%s>%s)' % (kind, pattern)))
        rexp = r'(?P<delimiter>%s)(?:%s)' % (re.escape(cls.delimiter),
                                             '|'.join(alters))
        cls.pattern = re.compile(rexp, re.IGNORECASE | re.VERBOSE)
        cls.factories = factories


class Template(metaclass=_TemplateClass):
    '''
    A string class for supporting $-substitutions.

    It has similar interface that `string.Template` but using "eval" instead
    simple dictionary looking.

    This means that you get all the functionality provided by `string.Template`
    (although, perhaps modified) and you get also the ability to write more
    complex expressions.

    If you need repetition or other flow-control sentences you should use
    other templating system.

    If you enclose and expression within ``${?...}`` it will be evaluated as a
    python expression. Simple variables are allowed just with ``$var`` or
    ``${var}``::

        >>> tpl = Template(str('${?1 + 1} is 2, and ${?x + x} is $x + ${x}'))
        >>> (tpl % dict(x=4)) == '2 is 2, and 8 is 4 + 4'
        True

    The mapping may be given by calling the template::

        >>> tpl(x=5) == '2 is 2, and 10 is 5 + 5'
        True
    '''

    delimiter = str('$')

    def __init__(self, template):
        self.template = template
        self.items = []
        pivot, valid = 0, True
        while valid:
            token = self.pattern.search(template, pivot)
            if token:
                start, end = token.span()
                if start > pivot:
                    self._append(template[pivot:start])
                factory, key = self._GetFactory(token)
                self._append(factory(self, key, start, end))
                pivot = end
            else:
                aux = template[pivot:]
                if aux:
                    self._append(aux)
                valid = False

    def __str__(self):
        return str('%s(%s)') % (self.__class__.__name__, self.template)

    def __call__(self, mapping={}, **kwargs):
        # TODO: Don't update if object
        kwargs.update(mapping)    # Don't modify mapping if given
        res = self.template.__class__()
        for item in self.items:
            if isinstance(item, _str_base):
                res += item
            else:
                res += item(kwargs)
        return res

    def __mod__(self, mapping):
        '''template % {'x':1}'''
        return self(mapping)

    def substitute(self, mapping={}, **kwargs):
        return self(mapping, **kwargs)

    def safe_substitute(self, mapping={}, **kwargs):
        # TODO: Don't update if object
        kwargs.update(mapping)    # Don't modify mapping if given
        res = self.template.__class__()
        for item in self.items:
            if isinstance(item, _str_base):
                res += item
            else:
                if item._unsafe:
                    res += item.match
                else:
                    try:
                        res += item(kwargs)
                    except Exception:  # TODO: @med which exceptions expected?
                        res += str('')    # item.match
        return res

    def _append(self, item):
        if (isinstance(item, _str_base) and
                self.items and isinstance(self.items[-1], _str_base)):
            self.items[-1] += item
        else:
            self.items.append(item)

    def _GetFactory(self, token):
        keys = list(self.factories)     # Get keys
        i, count = 0, len(keys)
        res = None
        while not res and (i < count):
            key = keys[i]
            aux = token.group(key)
            if aux is not None:
                res = self.factories[key]
            else:
                i += 1
        return res, aux


def count(source, chars):
    '''
    Counts how chars from `chars` are found in `source`::

        >>> count('Todos los nenes del mundo vamos una rueda a hacer', 'a')
        1

        # The vowel "i" is missing
        >>> count('Todos los nenes del mundo vamos una rueda a hacer', 'aeiuo')
        4
    '''
    res = 0
    for ch in chars:
        if ch in source:
            res += 1
    return res
