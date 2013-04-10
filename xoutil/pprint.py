#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.pprint
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
# Created on 8 avr. 2013

'''Support to pretty-print complex data structures.

Based on Fred L. Drake, Jr. <fdrake@acm.org>.

Very simple, but useful, especially in debugging data structures.

Classes
-------

PrettyPrinter()
    Handle pretty-printing operations onto a stream using a configured
    set of formatting parameters.

Functions
---------

pformat()
    Format a Python object into a pretty-printed representation.

pprint()
    Pretty-print a Python object to a stream [default is sys.stdout].

saferepr()
    Generate a 'standard' repr()-like value, but protect against recursive
    data structures.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

__docstring_format__ = 'rst'
__author__ = 'med'



import sys as _sys
from collections import OrderedDict as _OrderedDict
from io import StringIO as _StringIO

__all__ = [str(name) for name in ("pprint", "pformat", "isreadable",
                                  "isrecursive", "saferepr", "PrettyPrinter")]

# cache these for faster access:
_commajoin = ", ".join


def pprint(obj, stream=None, indent=1, width=80, depth=None):
    '''Pretty-print a Python object to a stream [default is sys.stdout].'''
    printer = PrettyPrinter(stream=stream, indent=indent, width=width,
                            depth=depth)
    printer.pprint(obj)


def pformat(obj, indent=1, width=80, depth=None):
    '''Format a Python object into a pretty-printed representation.'''
    return PrettyPrinter(indent=indent, width=width, depth=depth).pformat(obj)


def saferepr(obj):
    '''Version of repr() which can handle recursive data structures.'''
    return _safe_repr(obj, {}, None, 0)[0]


def isreadable(obj):
    '''Determine if saferepr(obj) is readable by eval().'''
    return _safe_repr(obj, {}, None, 0)[1]


def isrecursive(obj):
    '''Determine if obj requires a recursive representation.'''
    return _safe_repr(obj, {}, None, 0)[2]


class _safe_key:
    '''Helper function for key functions when sorting unorderable objects.

    The wrapped-obj will fallback to an Py2.x style comparison for
    unorderable types (sorting first comparing the type name and then by
    the obj ids).  Does not work recursively, so dict.items() must have
    _safe_key applied to both the key and the value.

    '''

    __slots__ = ['obj']

    def __init__(self, obj):
        self.obj = obj

    def __lt__(self, other):
        try:
            rv = self.obj.__lt__(other.obj)
        except TypeError:
            rv = NotImplemented

        if rv is NotImplemented:
            rv = (str(type(self.obj)), id(self.obj)) < \
                 (str(type(other.obj)), id(other.obj))
        return rv


def _safe_tuple(t):
    "Helper function for comparing 2-tuples"
    return _safe_key(t[0]), _safe_key(t[1])


class PrettyPrinter(object):
    def __init__(self, indent=1, width=80, depth=None, stream=None):
        '''Handle pretty printing operations onto a stream using a set of
        configured parameters.

        indent
            Number of spaces to indent for each level of nesting.

        width
            Attempted maximum number of columns in the output.

        depth
            The maximum depth to print out nested structures.

        stream
            The desired output stream.  If omitted (or false), the standard
            output stream available at construction will be used.

        '''
        indent = int(indent)
        width = int(width)
        assert indent >= 0, "indent must be >= 0"
        assert depth is None or depth > 0, "depth must be > 0"
        assert width, "width must be != 0"
        self._depth = depth
        self._indent_per_level = indent
        self._width = width
        if stream is not None:
            self._stream = stream
        else:
            self._stream = _sys.stdout

    def pprint(self, obj):
        self._format(obj, self._stream, 0, 0, {}, 0)
        self._stream.write("\n")

    def pformat(self, obj):
        sio = _StringIO()
        self._format(obj, sio, 0, 0, {}, 0)
        return sio.getvalue()

    def isrecursive(self, obj):
        return self.format(obj, {}, 0, 0)[2]

    def isreadable(self, obj):
        _s, readable, recursive = self.format(obj, {}, 0, 0)
        return readable and not recursive

    def _format(self, obj, stream, indent, allowance, context, level):
        level = level + 1
        objid = id(obj)
        if objid in context:
            stream.write(_recursion(obj))
            self._recursive = True
            self._readable = False
            return
        rep = self._repr(obj, context, level - 1)
        typ = type(obj)
        sepLines = len(rep) > (self._width - 1 - indent - allowance)
        write = stream.write

        if self._depth and level > self._depth:
            write(rep)
            return

        if sepLines:
            r = getattr(typ, "__repr__", None)
            if issubclass(typ, dict):
                write('{')
                if self._indent_per_level > 1:
                    write((self._indent_per_level - 1) * ' ')
                length = len(obj)
                if length:
                    context[objid] = 1
                    indent = indent + self._indent_per_level
                    if issubclass(typ, _OrderedDict):
                        items = list(obj.items())
                    else:
                        items = sorted(obj.items(), key=_safe_tuple)
                    key, ent = items[0]
                    rep = self._repr(key, context, level)
                    write(rep)
                    write(': ')
                    self._format(ent, stream, indent + len(rep) + 2,
                                  allowance + 1, context, level)
                    if length > 1:
                        for key, ent in items[1:]:
                            rep = self._repr(key, context, level)
                            write(',\n%s%s: ' % (' '*indent, rep))
                            self._format(ent, stream, indent + len(rep) + 2,
                                          allowance + 1, context, level)
                    indent = indent - self._indent_per_level
                    del context[objid]
                write('}')
                return

            if ((issubclass(typ, list) and r is list.__repr__) or
                (issubclass(typ, tuple) and r is tuple.__repr__) or
                (issubclass(typ, set) and r is set.__repr__) or
                (issubclass(typ, frozenset) and r is frozenset.__repr__)
               ):
                length = len(obj)
                if issubclass(typ, list):
                    write('[')
                    endchar = ']'
                elif issubclass(typ, set):
                    if not length:
                        write('set()')
                        return
                    write('{')
                    endchar = '}'
                    obj = sorted(obj, key=_safe_key)
                elif issubclass(typ, frozenset):
                    if not length:
                        write('frozenset()')
                        return
                    write('frozenset({')
                    endchar = '})'
                    obj = sorted(obj, key=_safe_key)
                    indent += 10
                else:
                    write('(')
                    endchar = ')'
                if self._indent_per_level > 1:
                    write((self._indent_per_level - 1) * ' ')
                if length:
                    context[objid] = 1
                    indent = indent + self._indent_per_level
                    self._format(obj[0], stream, indent, allowance + 1,
                                 context, level)
                    if length > 1:
                        for ent in obj[1:]:
                            write(',\n' + ' '*indent)
                            self._format(ent, stream, indent,
                                          allowance + 1, context, level)
                    indent = indent - self._indent_per_level
                    del context[objid]
                if issubclass(typ, tuple) and length == 1:
                    write(',')
                write(endchar)
                return

        write(rep)

    def _repr(self, obj, context, level):
        repr, readable, recursive = self.format(obj, context.copy(),
                                                self._depth, level)
        if not readable:
            self._readable = False
        if recursive:
            self._recursive = True
        return repr

    def format(self, obj, context, maxlevels, level):
        '''Format object for a specific context, returning a string
        and flags indicating whether the representation is 'readable'
        and whether the object represents a recursive construct.
        '''
        return _safe_repr(obj, context, maxlevels, level)


# Return triple (repr_string, isreadable, isrecursive).

def _safe_repr(obj, context, maxlevels, level):
    typ = type(obj)
    if typ is str:
        if 'locale' not in _sys.modules:
            return repr(obj), True, False
        if "'" in obj and '"' not in obj:
            closure = '"'
            quotes = {'"': '\\"'}
        else:
            closure = "'"
            quotes = {"'": "\\'"}
        qget = quotes.get
        sio = _StringIO()
        write = sio.write
        for char in obj:
            if char.isalpha():
                write(char)
            else:
                write(qget(char, repr(char)[1:-1]))
        return ("%s%s%s" % (closure, sio.getvalue(), closure)), True, False

    r = getattr(typ, "__repr__", None)
    if issubclass(typ, dict) and r is dict.__repr__:
        if not obj:
            return "{}", True, False
        objid = id(obj)
        if maxlevels and level >= maxlevels:
            return "{...}", False, objid in context
        if objid in context:
            return _recursion(obj), False, True
        context[objid] = 1
        readable = True
        recursive = False
        components = []
        append = components.append
        level += 1
        saferepr = _safe_repr
        items = sorted(obj.items(), key=_safe_tuple)
        for k, v in items:
            krepr, kreadable, krecur = saferepr(k, context, maxlevels, level)
            vrepr, vreadable, vrecur = saferepr(v, context, maxlevels, level)
            append("%s: %s" % (krepr, vrepr))
            readable = readable and kreadable and vreadable
            if krecur or vrecur:
                recursive = True
        del context[objid]
        return "{%s}" % _commajoin(components), readable, recursive

    if (issubclass(typ, list) and r is list.__repr__) or \
       (issubclass(typ, tuple) and r is tuple.__repr__):
        if issubclass(typ, list):
            if not obj:
                return "[]", True, False
            format = "[%s]"
        elif len(obj) == 1:
            format = "(%s,)"
        else:
            if not obj:
                return "()", True, False
            format = "(%s)"
        objid = id(obj)
        if maxlevels and level >= maxlevels:
            return format % "...", False, objid in context
        if objid in context:
            return _recursion(obj), False, True
        context[objid] = 1
        readable = True
        recursive = False
        components = []
        append = components.append
        level += 1
        for o in obj:
            orepr, oreadable, orecur = _safe_repr(o, context, maxlevels, level)
            append(orepr)
            if not oreadable:
                readable = False
            if orecur:
                recursive = True
        del context[objid]
        return format % _commajoin(components), readable, recursive

    rep = repr(obj)
    return rep, (rep and not rep.startswith('<')), False


def _recursion(obj):
    return ("<Recursion on %s with id=%s>"
            % (type(obj).__name__, id(obj)))
