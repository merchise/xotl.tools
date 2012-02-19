#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.pep3124
#----------------------------------------------------------------------
# Copyright (c) 2011 Merchise Autrement
# All rights reserved.
#
# Author: Manuel Vázquez Acosta
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
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
# Created on 2011-11-08

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

"An implementation of the @overload decorator for python 2.7"

__docstring_format__ = 'rst'
__version__ = '0.1.0'
__author__ = 'Manuel Vázquez Acosta <mva.led@gmail.com>'

from functools import wraps
from xoutil.types import Unset
from xoutil.iterators import first
from collections import OrderedDict as odict

class OverloadError(Exception):
    pass

# TODO: Comply with PEP 3124

# TODO: Make it work with methods
class overload(object):
    '''A decorator for overloading functions.

    This is not being designed to work with methods. This is inspired in
    the overload PEP 3124.

    Overloading just takes care of selecting the appropriate function definition
    from inspecting the types of the arguments.

    For instance, if you need to write a function that may accept either a
    string or a class as its first argument, you may split the function into two
    separate definitions like this::

       >>> @overload(basestring)
       ... def myfunc(string, *args):
       ...     return 'basestring'

       >>> @overload(type)
       ... def myfunc(cls, *args):
       ...     return 'type'

    This simply creates a `myfunc` function that upon invokation will check the
    type of its first argument and execute the original matching function::

        >>> myfunc('Just to show off')
        'basestring'

        >>> class X(object): pass
        >>> myfunc(X)
        'type'

    If you try to call an overloaded function and it can't find a match
    for the arguments' types, it will raise an OverloadError::

        >>> myfunc(1.2)
        Traceback (most recent call last):
            ...
        OverloadError: Impossible to find a matching overload.
    '''

    # TODO: Generalizar un árbol de decisión.
    class _tree(object):
        'A very simplified decision tree (by type) implementation'
        def __init__(self, payload=None):
            self.children = odict()
            self.payload = payload

        def walk_to_path(self, path, build=False):
            if path == tuple():
                return self

            child = first(lambda child: issubclass(path[0], child), self.children, None)
            if child:
                return self.children[child].walk_to_path(path[1:], build)
            if child is None and build:
                child = self.__class__()
                self.children[path[0]] = child
                return child.walk_to_path(path[1:], build)

    _overloads = odict()

    @classmethod
    def _cleanup(cls):
        'Clears all overloaded functions. Only useful for testing purposes.'
        cls._overloads = odict()

    def __new__(self, *types):
        def decorator(fun):
            import inspect
            module = inspect.getmodule(fun)
            fkey = (inspect.getmodulename(module.__file__), fun.__name__,)
            @wraps(fun)
            def inner(*args):
                types = tuple(type(arg) for arg in args)
                tree = inner.__decision_tree__
                node = tree.walk_to_path(types)
                if node and getattr(node, 'payload', None):
                    return node.payload(*args)
                else:
                    raise OverloadError, 'Impossible to find a matching overload.'

            if fkey not in self._overloads:
                self._overloads[fkey] = inner
            result = self._overloads[fkey]
            __decision_tree__ = getattr(result, '__decision_tree__', self._tree())
            node = __decision_tree__.walk_to_path(types, build=True)
            if node.payload:
                raise OverloadError, 'Conflicting overloading patterns'
            else:
                node.payload = fun
            if getattr(result, '__decision_tree__', Unset) is Unset:
                setattr(result, '__decision_tree__', __decision_tree__)
            return result
        return decorator

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True, report=True)
