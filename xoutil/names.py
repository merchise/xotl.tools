#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''A protocol to obtain or manage object names.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

# FIX: These imports must be local
from xoutil.symbols import Undefined as _undef
from xoutil.eight import base_string


# TODO: This module must be reviewed and deprecate most of it.

def _get_mappings(source):
    '''Return a sequence of mappings from `source`.

    Source could be a stack frame, a single dictionary, or any sequence of
    dictionaries.

    '''
    from collections import Mapping
    if isinstance(source, Mapping):
        return (source,)
    else:
        from xoutil.future.inspect import get_attr_value
        l = get_attr_value(source, 'f_locals', _undef)
        g = get_attr_value(source, 'f_globals', _undef)
        if isinstance(l, Mapping) and isinstance(g, Mapping):
            return (l,) if l is g else (l, g)
        else:
            return tuple(source)


def _key_for_value(source, value, strict=True):
    '''Returns the tuple (key, mapping) where the "value" is found.

    if strict is True, then look first for the same object::
        >>> x = [1]
        >>> y = [1]  #  equal to `x` but not the same
        >>> src = {'x': x, 'y': y}
        >>> search = lambda o, strict=True: _key_for_value(src, o, strict)
        >>> search(x) == search(y)
        False
        >>> search(x, strict=False) == search(y, strict=False)
        True

    This is mainly intended to find object names in stack frame variables.

    Source could be a stack frame, a single dictionary, or any sequence of
    dictionaries.

    '''
    source = _get_mappings(source)
    found, equal = _undef, (None, {})
    i, mapping_count = 0, len(source)
    while found is _undef and (i < mapping_count):
        mapping = source[i]
        keys = list(mapping)
        j, key_count = 0, len(keys)
        while found is _undef and (j < key_count):
            key = keys[j]
            item = mapping[key]
            if item is value:
                found = key, mapping
            elif item == value:
                if strict:
                    equal = key, mapping
                else:
                    found = key, mapping
            j += 1
        i += 1
    return found if found is not _undef else equal


def _get_value(source, key, default=None):
    '''Returns the value for the given `key` in `source` mappings.

    This is mainly intended to obtain object values in stack frame variables.

    Source could be a stack frame, a single dictionary, or any sequence of
    dictionaries.

    '''
    source = _get_mappings(source)
    res = _undef
    i, mapping_count = 0, len(source)
    while res is _undef and (i < mapping_count):
        mapping = source[i]
        res = mapping.get(key, _undef)
        i += 1
    return res if res is not _undef else default


def _get_best_name(names, safe=False, full=False):
    '''Get the best name in the give list of `names`.

    Best names are chosen in the following order (from worst to best):

    - Any string
    - A valid slug
    - A valid protected identifier
    - A valid public identifier
    - A valid full identifier

    If a string in the list `names` contains the substring "%(next)s", then
    the algorithm recurses to find the best name of the remaining names first
    and substitutes the substring with the result, the remaining names are
    then pruned from the search.

    If `safe` is True, returned name must be a valid identifier.  If `full` is
    True (halted if `safe` is not True) then the returned name must a valid
    full identifier.

    '''
    from xoutil.validators import (is_valid_full_identifier,
                                   is_valid_public_identifier,
                                   is_valid_identifier,
                                   is_valid_slug)
    names = list(names)

    def inner(start=0):
        ok, best_idx, best_qlty = start, -1, 0
        i, count = start, len(names)
        assert start < count, 'start is "%s", max is "%s".' % (start, count)
        while i < count:
            name = names[i]
            if '%(next)s' in name:
                next = inner(i + 1)
                names[i] = name % {'next': next}
                count = i + 1
            else:
                if is_valid_slug(name):
                    qlty = 25
                if is_valid_identifier(name):
                    qlty = 75 if is_valid_public_identifier(name) else 50
                elif is_valid_full_identifier(name):
                    qlty = 100
                else:
                    qlty = -25
                if best_qlty <= qlty:
                    best_idx = i
                    best_qlty = qlty
                ok = i
                i += 1
        idx = best_idx if best_idx >= 0 else ok
        return names[idx]
    res = inner()
    if safe:
        # TODO: Improve these methods to return False of reserved identifiers
        is_valid = is_valid_full_identifier if full else is_valid_identifier
        if not is_valid(res):
            from xoutil.string import slugify
            _mark = 'dot_dot_dot'
            full = full and '.' in res
            if full:
                res = res.replace('.', _mark)
            res = slugify(res, '_')
            if full:
                res = res.replace(_mark, '.')
            if not is_valid(res):
                res = '_' + res
    return str(res)


def module_name(item):
    '''Returns the full module name where the given object is declared.

    Examples::

       >>> module_name(module_name)
       'xoutil.names'

       >>> from xoutil.symbols import Unset
       >>> module_name(Unset)
       'xoutil.symbols'

    '''
    from xoutil.future.inspect import get_attr_value
    if item is None:
        res = ''
    elif isinstance(item, base_string):
        res = item
    else:
        res = get_attr_value(item, '__module__', None)
        if res is None:
            res = get_attr_value(type(item), '__module__', '')
    if res.startswith('__') or res in ('builtins', 'exceptions', '<module>'):
        res = ''
    return str(res)


def simple_name(item, join=True):
    '''Returns the simple name for the given object.

    :param join: If False, only the object inner name is returned; if it is a
           callable is used similar to a string join receiving a tuple of
           (module-name, inner-name) as argument; True means (is equivalent
           to)::

             join = lambda arg: '.'.join(arg).strip('.')

           For example, use ``lambda arg: arg`` to return the 2-tuple itself.

           See `module_name`:func: for more information when a not False value
           is used.

    Examples::

       >>> simple_name(simple_name)
       'xoutil.names.simple_name'

       >>> from xoutil.symbols import Unset
       >>> simple_name(Unset)
       'xoutil.symbols.Unset'

    This function is intended for named objects (those with the `__name__`
    attribute), if an object without standard name is used, the type name is
    returned instead; for example::

        >>> simple_name(0)
        'int'

    To get a name in a more precise way, use `nameof`:func:.

    '''
    # TODO: deprecate `join` argument
    from xoutil.future.inspect import safe_name
    singletons = (None, True, False, Ellipsis, NotImplemented)
    res = next((str(s) for s in singletons if s is item), None)
    if res is None:
        res = safe_name(item)
        if res is None:
            item = type(item)
            res = safe_name(item)
        if join:
            if join is True:
                def join(arg):
                    return str('.'.join(arg).strip('.'))
            res = join((module_name(item), res))
    return res


def nameof(*args, **kwargs):
    '''Obtain the name of each one of a set of objects.

    .. versionadded:: 1.4.0

    .. versionchanged:: 1.6.0

       - Keyword arguments are now keyword-only arguments.

       - Support for several objects

       - Improved the semantics of parameter `full`.

       - Added the `safe` keyword argument.

    If no object is given, None is returned; if only one object is given, a
    single string is returned; otherwise a list of strings is returned.

    The name of an object is normally the variable name in the calling stack.

    If the object is not present calling frame, up to five frame levels are
    searched.  Use the `depth` keyword argument to specify a different
    starting point and the search will proceed five levels from this frame up.

    If the same object has several good names a single one is arbitrarily
    chosen.

    Good names candidates are retrieved based on the keywords arguments
    `full`, `inner`, `safe` and `typed`.

    If `typed` is True and the object is not a type name or a callable (see
    `xoutil.future.inspect.safe_name`:func:), then the `type` of the object is
    used instead.

    If `inner` is True we try to extract the name by introspection instead of
    looking for the object in the frame stack.

    If `full` is True the full identifier of the object is preferred.  In this
    case if `inner` is False the local-name for the object is found.  If
    `inner` is True, find the import-name.

    If `safe` is True, returned value is converted -if it is not- into a valid
    Python identifier, though you should not trust this identifier resolves to
    the value.

    See `the examples in the documentation <name-of-narrative>`:ref:.

    '''
    # XXX: The examples are stripped from here.  Go the documentation page.
    from numbers import Number
    from xoutil.eight import range
    from xoutil.future.inspect import safe_name
    arg_count = len(args)
    names = [[] for i in range(arg_count)]

    class vars:
        '`nonlocal` simulation'
        params = kwargs
        idx = 0

    def grant(name=None, **again):
        if name:
            names[vars.idx].append(name)
            assert len(names[vars.idx]) < 5
        if again:
            vars.params = dict(kwargs, **again)
        else:
            vars.params = kwargs
            vars.idx += 1

    def param(name, default=False):
        return vars.params.get(name, default)

    while vars.idx < arg_count:
        item = args[vars.idx]
        if param('typed') and not safe_name(item):
            item = type(item)
        if param('inner'):
            res = safe_name(item)
            if res:
                if param('full'):
                    head = module_name(item)
                    if head:
                        res = '.'.join((head, res))
                grant(res)
            elif isinstance(item, (base_string, Number)):
                grant(str(item))
            else:
                grant('@'.join(('%(next)s', hex(id(item)))), typed=True)
        else:
            import sys
            sf = sys._getframe(param('depth', 1))
            try:
                i, LIMIT, res = 0, 5, _undef
                _full = param('full')
                while not res and sf and (i < LIMIT):
                    key, mapping = _key_for_value(sf, item)
                    if key and _full:
                        head = module_name(_get_value(mapping, '__name__'))
                        if not head:
                            head = module_name(sf.f_code.co_name)
                        if not head:
                            head = module_name(item) or None
                    else:
                        head = None
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
                grant('.'.join((head, res)) if head else res)
            else:
                res = safe_name(item)
                if res:
                    grant(res)
                else:
                    grant(None, inner=True)
    for i in range(arg_count):
        names[i] = _get_best_name(names[i], safe=param('safe'))
    if arg_count == 0:
        return None
    elif arg_count == 1:
        return names[0]
    else:
        return names


def identifier_from(*args):
    '''Build an valid identifier from the name extracted from an object.

    .. versionadded:: 1.5.6

    First, check if argument is a type and then returns the name of the type
    prefixed with `_` if valid; otherwise calls `nameof` function repeatedly
    until a valid identifier is found using the following order logic:
    ``inner=True``, without arguments looking-up a variable in the calling
    stack, and ``typed=True``.  Returns None if no valid value is found.

    Examples::

        >>> identifier_from({})
        'dict'

    '''
    if len(args) == 1:
        from xoutil.validators.identifiers import is_valid_identifier as valid
        from xoutil.future.inspect import get_attr_value
        res = None
        if isinstance(args[0], type):
            aux = get_attr_value(args[0], '__name__', None)
            if valid(aux):
                res = str('_%s' % aux)
        if res is None:
            tests = ({'inner': True}, {}, {'typed': True})
            names = (nameof(args[0], depth=2, **test) for test in tests)
            res = next((name for name in names if valid(name)), None)
        return res
    else:
        msg = 'identifier_from() takes exactly 1 argument (%s given)'
        raise TypeError(msg % len(args))


class namelist(list):
    '''Similar to list, but only intended for storing object names.

    Constructors:

    * namelist() -> new empty list
    * namelist(collection) -> new list initialized from collection's items
    * namelist(item, ...) -> new list initialized from severals items

    Instances can be used as decorators to store names of module items
    (functions or classes)::

        >>> __all__ = namelist()
        >>> @__all__
        ... def foobar(*args, **kwargs):
        ...     'Automatically added to this module "__all__" names.'

        >>> 'foobar' in __all__
        True

    '''
    def __init__(self, *args):
        if len(args) == 1:
            from types import GeneratorType as gtype
            if isinstance(args[0], (tuple, list, set, frozenset, gtype)):
                args = args[0]
        super().__init__(nameof(arg, depth=2) for arg in args)

    def __add__(self, other):
        other = [nameof(item, depth=2) for item in other]
        return super().__add__(other)

    __iadd__ = __add__

    def __contains__(self, item):
        return super().__contains__(nameof(item, inner=True))

    def append(self, value):
        '''l.append(value) -- append a name object to end'''
        super().append(nameof(value, depth=2))
        return value    # What allow to use its instances as a decorator

    __call__ = append

    def extend(self, items):
        '''l.extend(items) -- extend list by appending items from the iterable
        '''
        items = (nameof(item, depth=2) for item in items)
        return super().extend(items)

    def index(self, value, *args):
        '''l.index(value, [start, [stop]]) -> int -- return first index of name

        Raises ValueError if the name is not present.

        '''
        return super().index(nameof(value, depth=2), *args)

    def insert(self, index, value):
        '''l.insert(index, value) -- insert object before index
        '''
        return super().insert(index, nameof(value, depth=2))

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
        super().__init__(str(arg) for arg in args)

    def __add__(self, other):
        other = [str(item) for item in other]
        return super().__add__(other)

    __iadd__ = __add__

    def __contains__(self, item):
        return super().__contains__(str(item))

    def append(self, value):
        '''l.append(value) -- append a name object to end'''
        super().append(str(value))
        return value    # What allow to use its instances as a decorator

    __call__ = append

    def extend(self, items):
        '''l.extend(items) -- extend list by appending items from the iterable
        '''
        items = (str(item) for item in items)
        return super().extend(items)

    def index(self, value, *args):
        '''l.index(value, [start, [stop]]) -> int -- return first index of name

        Raises ValueError if the name is not present.

        '''
        return super().index(str(value), *args)

    def insert(self, index, value):
        '''l.insert(index, value) -- insert object before index
        '''
        return super().insert(index, str(value))

    def remove(self, value):
        '''l.remove(value) -- remove first occurrence of value

        Raises ValueError if the value is not present.

        '''
        return list.remove(self, str(value))


# Theses tests need to be defined in this module to test relative imports.
# Otherwise the `tests/` directory would need to be a proper package.

import unittest as _utest
from xoutil.symbols import Unset as _Unset   # Use a tier 0 module!


class TestRelativeImports(_utest.TestCase):
    RelativeUnset = _Unset
    AbsoluteUndefined = _undef

    def test_relative_imports(self):
        self.assertEquals(nameof(self.RelativeUnset), '_Unset')
        self.assertEquals(nameof(self.RelativeUnset, inner=True), 'Unset')

        # Even relative imports are resolved properly with `full=True`
        self.assertEquals(nameof(self.RelativeUnset, full=True),
                          'xoutil.names._Unset')

        self.assertEquals(nameof(self.AbsoluteUndefined, full=True),
                          'xoutil.names._undef')


# Don't delete the _Unset name, so that the nameof inside the test could find
# them in the module.
del _utest
