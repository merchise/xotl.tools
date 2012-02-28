#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.formatter
#----------------------------------------------------------------------
# Copyright (c) 2009-2011 Merchise Autrement
# All rights reserved.
#
# Author: Medardo Rodriguez
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


'''Smart formatting.'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)


class DelimiterFactory(object):
    def __new__(cls, owner, key, start, end):
        return key


class BaseFactory(object):
    _unsafe = False

    def __init__(self, owner, key, start, end):
        self.key = key
        self.match = owner.template[start:end]
        self.start = start


class MapFactory(BaseFactory):
    def __call__(self, mapping):
        return unicode(mapping[self.key])


class PyFactory(BaseFactory):
    def __init__(self, owner, key, start, end):
        super(PyFactory, self).__init__(owner,
                                        compile(key, '', 'eval'),
                                        start, end)

    def __call__(self, mapping):
        return unicode(eval(self.key, mapping))


class InvalidFactory(object):
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
        raise ValueError('Invalid place-holder in string: line "%d", col "%d"' % (line, col))


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
        super(_TemplateClass, cls).__init__(name, bases, attrs)
        alters, factories = [], {}
        for kind, pattern, wrapper, factory in cls._alters:
            factories[kind] = factory
            alters.append(wrapper % ('(?P<%s>%s)' % (kind, pattern)))
        rexp = r'(?P<delimiter>%s)(?:%s)' % (re.escape(cls.delimiter), b'|'.join(alters))
        cls.pattern = re.compile(rexp, re.IGNORECASE | re.VERBOSE)
        cls.factories = factories


class Template(object):
    '''
    A string class for supporting $-substitutions.
    It has similar interface that "string.Template" but using "eval" instead
    simple dictionary looking.
    '''

    __metaclass__ = _TemplateClass

    delimiter = '$'

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
        return '%s(%s)' % (self.__class__.__name__, self.template)

    def __call__(self, mapping={}, **kwargs):
        # TODO: Don't update if object
        kwargs.update(mapping)    # Don't modify mapping if given
        res = self.template.__class__()
        for item in self.items:
            if isinstance(item, basestring):
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
            if isinstance(item, basestring):
                res += item
            else:
                if item._unsafe:
                    res += item.match
                else:
                    try:
                        res += item(kwargs)
                    except:
                        res += ''    # item.match
        return res

    def _append(self, item):
        if isinstance(item, basestring) and self.items and isinstance(self.items[-1], basestring):
            self.items[-1] += item
        else:
            self.items.append(item)

    def _GetFactory(self, token):
        keys = self.factories.keys()
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
