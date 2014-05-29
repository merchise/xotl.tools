#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.names
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 15 avr. 2013

'''A protocol to obtain or manage object names.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


try:
    str_base = basestring
except NameError:
    str_base = str


def _key_for_value(target, value, strict=True):
    '''Returns the key that has the "value" in dictionary "target".

    if strict is True, then look first for the same object::
        >>> from functools import partial
        >>> x = {1}
        >>> y = {1}
        >>> search = partial(_key_for_value, {'x': x, 'y': y})
        >>> search(x) == search(y)
        False
        >>> search(x, strict=False) == search(y, strict=False)
        True

    This is mainly intended to find object names in stack frame variables.

    '''
    keys = list(target)     # Get keys
    i, found, equal = 0, False, None
    while (i < len(keys)) and not found:
        key = keys[i]
        item = target[key]
        if item is value:
            found = key
        elif item == value:
            if strict:
                equal = key
                i += 1
            else:
                found = key
        else:
            i += 1
    return found or equal


def module_name(target):
    if target is None:
        target = ''
    elif isinstance(target, str_base):
        res = target
    else:
        res = getattr(target, '__module__', None)
        if res is None:
            res = getattr(type(target), '__module__', '')
    if res.startswith('__') or (res in ('builtins', '<module>')):
        res = ''
    return str(res)


def nameof(target, depth=1, inner=False, typed=False, full=False):
    '''Gets the name of an object.

    .. versionadded:: 1.4.0


    The name of an object is normally the variable name in the calling stack::

        >>> from xoutil.collections import OrderedDict as sorted_dict
        >>> nameof(sorted_dict)
        'sorted_dict'

    If the `inner` flag is true, then the name is found by introspection
    first::

        >>> nameof(sorted_dict, inner=True)
        'OrderedDict'

    If the `typed` flag is true, returns the name of the type unless `target`
    is already a type or it has a "__name__" attribute, but the "__name__" is
    used only if `inner` is True.

        >>> sd = sorted_dict(x=1, y=2)
        >>> nameof(sd)
        'sd'

        >>> nameof(sd, typed=True)
        'sorted_dict'

        >>> nameof(sd, inner=True, typed=True)
        'OrderedDict'

    If `target` is an instance of a simple type (strings or numbers) and
    `inner` is true, then the name is the standard representation of `target`::

        >>> s = 'foobar'
        >>> nameof(s)
        's'

        >>> nameof(s, inner=True)
        'foobar'

        >>> i = 1
        >>> nameof(i)
        'i'

        >>> nameof(i, inner=True)
        '1'

        >>> nameof(i, typed=True)
        'int'

    If `target` isn't an instance of a simple type (strings or numbers) and
    `inner` is true, then the id of the object is used::

        >>> hex(id(sd)) in nameof(sd, inner=True)
        True

    If `full` is True, then the module where the name is imported is prefixed.
    If `inner` is True at the same time, then the full module where the item
    is defined (if it's exists) is returned.

    Examples::

        >>> nameof(sd, full=True)
        'xoutil.names.sd'

        >>> nameof(sd, typed=True, full=True)
        'xoutil.names.sorted_dict'

    :param depth: Amount of stack levels to skip if needed.

    .. warning:: Some times `full` True automatically implied `inner` to be
       true as well.  For instance in our tests for this module we have
       something like this::

         from xoutil.collections import OrderedSmartDict

         def test_module_level_name():
             from xoutil.names import nameof
             assert nameof(OrderedSmartDict, full=True) == 'xoutil.collections.OrderedSmartDict'

       Notice that in that case the returned name contains where the name was
       defined and not where it was imported as it documented before.

       This actually happens in the case that the object is not imported in
       the same frame stack calling `nameof`:func:.  We traverse the stack
       forcing `inner` to be True to avoid infinite recursion.

       In `xoutil 1.6.0` this has been corrected but then the behavior is not
       backwards compatible.

    '''
    from numbers import Number
    TYPED_NAME = '__name__'
    if typed and not hasattr(target, TYPED_NAME):
        target = type(target)
    if inner:
        res = getattr(target, TYPED_NAME, False)
        if res:
            if full:
                head = module_name(target)
                if head:
                    res = '.'.join((head, res))
            return str(res)
        elif isinstance(target, (str_base, Number)):
            return str(target)
        else:
            type_name = nameof(target, depth=depth,
                               inner=True, typed=True, full=full)
            return str('@'.join((type_name, hex(id(target)))))
    else:
        import sys
        sf = sys._getframe(depth)
        try:
            res = False
            i, LIMIT = 0, 5   # Limit number of stack to recurse
            def getter(src):
                key = _key_for_value(l, target)
                if key and full:
                    head = src.get('__name__')
                    if not head:
                        head = sf.f_code.co_name
                    head = module_name(head)
                    if not head:
                        head = module_name(target) or None
                else:
                    head = None
                return key, head
            while not res and sf and (i < LIMIT):
                l = sf.f_locals
                key, head = getter(l)
                if not key:
                    g = sf.f_globals
                    if l is not g:
                        key, head = getter(g)
                if key:
                    res = key
                else:
                    sf = sf.f_back
                    i += 1
        finally:
            # TODO: on "del sf" Python says "SyntaxError: can not delete
            # variable 'sf' referenced in nested scope".
            sf = None
        if res:
            return str('.'.join((head, res)) if head else res)
        else:
            return nameof(target, depth=depth+1, inner=True, full=full)


class namelist(list):
    '''Similar to list, but only intended for storing object names.

    Constructors:

    * namelist() -> new empty list
    * namelist(collection) -> new list initialized from collection's items
    * namelist(item, ...) -> new list initialized from severals items

    Instances can be used as decorators to store names of module items
    (functions or classes).

    '''
    def __init__(self, *args):
        if len(args) == 1:
            from types import GeneratorType as gtype
            if isinstance(args[0], (tuple, list, set, frozenset, gtype)):
                args = args[0]
        super(namelist, self).__init__(nameof(arg, depth=2) for arg in args)

    def __add__(self, other):
        other = [nameof(item, depth=2) for item in other]
        return super(namelist, self).__add__(other)
    __iadd__ = __add__

    def __contains__(self, target):
        return super(namelist, self).__contains__(nameof(target, depth=2))

    def append(self, value):
        '''l.append(value) -- append a name object to end'''
        super(namelist, self).append(nameof(value, depth=2))
        return value    # What allow to use its instances as a decorator
    __call__ = append

    def extend(self, items):
        '''l.extend(items) -- extend list by appending items from the iterable
        '''
        items = (nameof(item, depth=2) for item in items)
        return super(namelist, self).extend(items)

    def index(self, value, *args):
        '''l.index(value, [start, [stop]]) -> int -- return first index of name

        Raises ValueError if the name is not present.

        '''
        return super(namelist, self).index(nameof(value, depth=2), *args)

    def insert(self, index, value):
        '''l.insert(index, value) -- insert object before index
        '''
        return super(namelist, self).insert(index, nameof(value, depth=2))

    def remove(self, value):
        '''l.remove(value) -- remove first occurrence of value

        Raises ValueError if the value is not present.

        '''
        return list.remove(self, nameof(value, depth=2))


class strlist(list):
    '''Similar to list, but only intended for storing ``str`` instances.

    Constructors:
        * strlist() -> new empty list
        * strlist(collection) -> new list initialized from collection's items
        * strlist(item, ...) -> new list initialized from severals items

    Last versions of Python 2.x has a feature to use unicode as standard
    strings, but some object names can be only ``str``. To be compatible with
    Python 3.x in an easy way, use this list.

    '''
    def __init__(self, *args):
        if len(args) == 1:
            from types import GeneratorType as gtype
            if isinstance(args[0], (tuple, list, set, frozenset, gtype)):
                args = args[0]
        super(strlist, self).__init__(str(arg) for arg in args)

    def __add__(self, other):
        other = [str(item) for item in other]
        return super(strlist, self).__add__(other)
    __iadd__ = __add__

    def __contains__(self, target):
        return super(strlist, self).__contains__(str(target))

    def append(self, value):
        '''l.append(value) -- append a name object to end'''
        super(strlist, self).append(str(value))
        return value    # What allow to use its instances as a decorator
    __call__ = append

    def extend(self, items):
        '''l.extend(items) -- extend list by appending items from the iterable
        '''
        items = (str(item) for item in items)
        return super(strlist, self).extend(items)

    def index(self, value, *args):
        '''l.index(value, [start, [stop]]) -> int -- return first index of name

        Raises ValueError if the name is not present.

        '''
        return super(strlist, self).index(str(value), *args)

    def insert(self, index, value):
        '''l.insert(index, value) -- insert object before index
        '''
        return super(strlist, self).insert(index, str(value))

    def remove(self, value):
        '''l.remove(value) -- remove first occurrence of value

        Raises ValueError if the value is not present.

        '''
        return list.remove(self, str(value))
