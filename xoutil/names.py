#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.names
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
# Created on 15 avr. 2013

'''A protocol to obtain or manage object names.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

__docstring_format__ = 'rst'
__author__ = 'med'


def nameof(target, force_type=False, depth=1):
    '''Gets the name of an object.

    - The name of a function or a class (an object with a ``__name__``
      attribute) is its value::

       >>> nameof(type)
       'type'

       >>> class Someclass:
       ...     pass
       >>> nameof(Someclass)
       'Someclass'

    - Other objects are looked up in the stack locals and globals definitions::

       >>> x, y = 1, '2'
       >>> nameof(1)
       'x'
       >>> nameof('2')
       'y'

    - For values not in previous cases:

      * If it's ``None``, is the empty string::

          >>> nameof(None)
          ''

      * If instance of a string is the same string::

          >>> nameof('manuel')
          'manuel'

      * If instance of a number is the same number as string::

          >>> nameof(1.1)
          '1.1'

      * Other values is ``id(%s) % id(target)::

          >>> x = object()
          >>> str(id(x)) in nameof(x)
          True

    - If ``force_type is True``, then it tries the type of the object if not
      a type or a string::

        >>> nameof([1, 2], force_type=True)
        'list'

        >>> nameof((1, 2), force_type=True)
        'tuple'

        >>> nameof({}, force_type=True)
        'dict'

        >>> # Strings are exceptions because it's considered that values are
        >>> # already converted to names
        >>> nameof('foobar', force_type=True)
        'foobar'

    - :param:`depth`: level of stack frames to start looking up, if needed.

    '''
    if hasattr(target, '__name__'):
        return target.__name__
    else:
        from xoutil.compat import str_base
        if force_type:
            if isinstance(target, str_base):
                return str(target)      # Just in case
            else:
                return type(target).__name__
        else:
            import sys
            try:
                from xoutil.collections import dict_key_for_value as search
                sf = sys._getframe(depth)
                res = False
                i, LIMIT = 0, 5   # Limit number of stack to recurse
                while not res and sf and (i < LIMIT):
                    key = search(sf.f_globals, target)
                    if key:
                        res = key
                    else:
                        sf = sf.f_back
                        i =+ 1
            except Exception as error:
                print('ERROR:', type(error), '::', error, file=sys.stderr)
                res = None
                raise
            if res:
                return str(res)
            else:
                from numbers import Number
                if isinstance(target, (str_base, Number)):
                    return str(target)
                else:
                    return str('id(%s)' % id(target))


class namelist(list):
    '''Similar to list, but only intended for storing object names.

    Constructors:
        * namelist() -> new empty list
        * namelist(collection) -> new list initialized from collection's items
        * namelist(item, ...) -> new list initialized from severals items

    Instances can be used as decorator to store names of module items
    (functions or classes)::
        >>> __all__ = namelist()
        >>> @__all__
        ... def foobar(*args, **kwargs):
        ...     'Automatically added to this module "__all__" names.'

    '''
    def __init__(self, *args):
        if len(args) == 1:
            from types import GeneratorType as gtype
            if isinstance(args[0], (tuple, list, set, frozenset, gtype)):
                args = args[0]
        super(namelist, self).__init__((nameof(arg) for arg in args))

    def __add__(self, other):
        other = [nameof(item) for item in other]
        return super(namelist, self).__add__(other)
    __iadd__ = __add__

    def __contains__(self, target):
        return super(namelist, self).__contains__(nameof(target))

    def append(self, value):
        '''l.append(value) -- append a name object to end'''
        super(namelist, self).append(nameof(value))
        return value    # What allow to use its instances as a decorator
    __call__ = append

    def extend(self, items):
        '''l.extend(items) -- extend list by appending items from the iterable
        '''
        items = (nameof(item) for item in items)
        return super(namelist, self).extend(items)

    def index(self, value, *args):
        '''l.index(value, [start, [stop]]) -> int -- return first index of name

        Raises ValueError if the name is not present.

        '''
        return super(namelist, self).index(nameof(value), *args)

    def insert(self, index, value):
        '''l.insert(index, value) -- insert object before index
        '''
        return super(namelist, self).insert(index, nameof(value))

    def remove(self, value):
        '''l.remove(value) -- remove first occurrence of value

        Raises ValueError if the value is not present.

        '''
        return list.remove(self, nameof(value))


__all__ = namelist(nameof, namelist)
