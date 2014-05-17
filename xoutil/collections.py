# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# xoutil.collections
# ----------------------------------------------------------------------
# Copyright 2013, 2014 Merchise Autrement and Contributors for the
# defaultdict and opendict implementations.
#
# Copyright 2012 Medardo Rodríguez for the defaultdict and opendict
# implementations.
#
# The implementation of OrderedDict is the copyright of the Python
# Software Foundation.
#
# This file is distributed under the terms of the LICENCE distributed
# with this package.
#
# @created: 2012-07-03
#
# Contributors from Medardo Rodríguez:
#    - Manuel Vázquez Acosta <manu@merchise.org>
#    - Medardo Rodriguez <med@merchise.org>


'''Extensions to Python's ``collections`` module.

You may use it as drop-in replacement of ``collections``. Although we don't
document all items here. Refer to :mod:`collections <collections>`
documentation.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)

import sys
from xoutil.modules import copy_members as _copy_python_module_members
_pm = _copy_python_module_members()

if sys.version_info >= (3, 3):
    _copy_python_module_members('collections.abc')
del sys

namedtuple = _pm.namedtuple
MutableMapping = _pm.MutableMapping
Mapping = _pm.Mapping
MutableSequence = _pm.MutableSequence
Sequence = _pm.Sequence
_itemgetter = _pm._itemgetter
_heapq = _pm._heapq
_chain = _pm._chain
_repeat = _pm._repeat
_starmap = _pm._starmap

del _pm, _copy_python_module_members


from collections import defaultdict as _defaultdict
from xoutil.names import strlist as slist
from xoutil.objects import SafeDataItem as safe


import sys
_py33 = sys.version_info >= (3, 3, 0)
_py34 = sys.version_info >= (3, 4, 0)
del sys


class defaultdict(_defaultdict):
    '''A hack for ``collections.defaultdict`` that passes the key and a copy of
    self as a plain dict (to avoid infinity recursion) to the callable.

    Examples::

        >>> from xoutil.collections import defaultdict
        >>> d = defaultdict(lambda key, d: 'a')
        >>> d['abc']
        'a'

        >>> d['abc'] = 1
        >>> d['abc']
        1

    Since the second parameter is actually a dict-copy, you may (naively) do
    the following::

        >>> d = defaultdict(lambda k, d: d[k])
        >>> d['abc']
        Traceback (most recent call last):
            ...
        KeyError: 'abc'


    You may use this class as a drop-in replacement for
    ``collections.defaultdict``::

        >>> d = defaultdict(lambda: 1)
        >>> d['abc']
        1

    '''
    def __missing__(self, key):
        if self.default_factory is not None:
            try:
                return self.default_factory(key, dict(self))
            except TypeError:
                # This is the error when the arguments are not expected.
                return super(defaultdict, self).__missing__(key)
        else:
            raise KeyError(key)


class OpenDictMixin(object):
    '''A mixin for mappings implementation that expose keys as attributes::

        >>> from xoutil.objects import SafeDataItem as safe

        >>> class MyOpenDict(OpenDictMixin, dict):
        ...     __slots__ = safe.slot(OpenDictMixin.__cache_name__, dict)

        >>> d = MyOpenDict({'es': 'spanish'})
        >>> d.es
        'spanish'

        >>> d['es'] = 'espanol'
        >>> d.es
        'espanol'

    When setting or deleting an attribute, the attribute name is regarded as
    key in the mapping if neither of the following condition holds:

    - The name is a `slot`.

    - The object has a ``__dict__`` attribute and the name is key there.

    This mixin defines the following features that can be redefined:

    _key2identifier

        Protected method, receive a key as argument and return a valid
        identifier that is used instead the key as an extended attribute.

    __cache_name__

        Inner field to store a cached mapping between actual keys and
        calculated attribute names.  The field must be always implemented as a
        `SafeDataItem` descriptor and must be of type `dict`.  There are two
        ways of implementing this:

        - As a slot.  The first time of this implementation is an example.
          Don't forget to pass the second parameter with the constructor
          `dict`.

        - As a normal descriptor::

            >>> from xoutil.objects import SafeDataItem as safe
            >>> class MyOpenDict(OpenDictMixin, dict):
            ...     safe(OpenDictMixin.__cache_name__, dict)


    Classes or Mixins that can be integrated with `dict` by inheritance
        must not have a `__slots__` definition.  Because of that, this mixin
        must not declare any slot.  If needed, it must be declared explicitly
        in customized classed like in the example in the first part of this
        documentation or in the definition of `opendict` class.

    '''
    __cache_name__ = str('_inverted_cache')

    def __dir__(self):
        '''Return normal "dir" plus valid keys as attributes.'''
        # TODO: Check if super must be called if defined
        from xoutil.objects import fulldir
        return list(set(~self) | fulldir(self))

    def __getattr__(self, name):
        from xoutil import Unset
        from xoutil.inspect import get_attr_value
        res = get_attr_value(self, name, Unset)
        if res is not Unset:
            return res
        else:
            key = (~self).get(name)
            if key:
                return self[key]
            else:
                msg = "'%s' object has no attribute '%s'"
                raise AttributeError(msg % (type(self).__name__, name))

    def __setattr__(self, name, value):
        key = (~self).get(name)
        if key:
            self[key] = value
        else:
            super(OpenDictMixin, self).__setattr__(name, value)

    def __delattr__(self, name):
        key = (~self).get(name)
        if key:
            del self[key]
        else:
            super(OpenDictMixin, self).__delattr__(name)

    def __invert__(self):
        '''Return an inverted mapping between key and attribute names (keys of
        the resulting dictionary are identifiers for attribute names and values
        are original key names).

        Class attribute "__separators__" are used to calculate it and is
        cached in '_inverted_cache slot safe variable.

        Several keys could have the same identifier, only one will be valid and
        used.

        To obtain this mapping you can use as the unary operator "~".

        '''
        from xoutil.inspect import get_attr_value
        KEY_LENGTH = 'length'
        KEY_MAPPING = 'mapping'
        cache = get_attr_value(self, type(self).__cache_name__)
        cached_length = cache.setdefault(KEY_LENGTH, 0)
        length = len(self)
        if cached_length != length:
            cache[KEY_LENGTH] = length
            aux = ((self._key2identifier(k), k) for k in self)
            res = {key: attr for key, attr in aux if key}
            cache[KEY_MAPPING] = res
        else:
            res = cache.get(KEY_MAPPING)
            if res is None:
                assert cached_length == 0
                res = {}
                cache[KEY_MAPPING] = res
        return res

    @staticmethod
    def _key2identifier(key):
        '''Convert keys to valid identifiers.

        This method could be redefined in sub-classes to change this feature.
        This function must return a valid identifier or None if the conversion
        is not possible.

        '''
        from xoutil.string import normalize_slug
        return normalize_slug(key, '_')


class SmartDictMixin(object):
    '''A mixin that extends the `update` method of dictionaries

    Standard method allow only one positional argument, this allow several.

    Note on using mixins in Python: method resolution order is calculated in
    the order of inheritance, if a mixin is defined to overwrite behavior
    already existent, use first that classes with it. See :class:`SmartDict`
    below.

    '''
    def update(self, *args, **kwargs):
        '''Update this dict from a set of iterables `args` and keyword values
        `kwargs`.

        Each positional argument could be:

        - another mapping (any object implementing "keys" and
          :meth:`~object.__getitem__` methods.

        - an iterable of (key, value) pairs.

        '''
        for arg in args:
            if hasattr(arg, 'keys') and hasattr(arg, '__getitem__'):
                for key in arg:
                    self[key] = arg[key]
            else:
                for key, value in arg:
                    self[key] = value
        for key in kwargs:
            self[key] = kwargs[key]

    def search(self, pattern):
        '''Return new mapping with items which key match a `pattern` regexp.

        This function always tries to return a valid new mapping of the same
        type of the caller instance.  If the constructor of corresponding type
        can't be called without arguments, then look up for a class
        variable named `__search_result_type__` or return a standard
        Python dictionary if not found

        '''
        from re import compile
        regexp = compile(pattern)
        cls = type(self)
        try:
            res = cls()
        except BaseException:
            from xoutil.inspect import get_attr_value
            creator = get_attr_value(cls, '__search_result_type__', None)
            res = creator() if creator else {}
        for key in self:
            if regexp.search(key):
                res[key] = self[key]
        return res


class SmartDict(SmartDictMixin, dict):
    '''A "smart" dictionary that can receive a wide variety of arguments.

    See :meth:`SmartDictMixin.update` and :meth:`SmartDictMixin.search`.

    '''
    def __init__(self, *args, **kwargs):
        super(SmartDict, self).__init__()
        self.update(*args, **kwargs)


class opendict(OpenDictMixin, dict, object):
    '''A dictionary implementation that mirrors its keys as attributes::

         >>> d = opendict({'es': 'spanish'})
         >>> d.es
         'spanish'

         >>> d['es'] = 'espanol'
         >>> d.es
         'espanol'

    Setting attributes *does not* makes them keys.

    '''
    __slots__ = safe.slot(OpenDictMixin.__cache_name__, dict)


if not _py33:
    # From this point below: Copyright (c) 2001-2013, Python Software
    # Foundation; All rights reserved.

    import sys as _sys
    from weakref import proxy as _proxy
    from xoutil.reprlib import recursive_repr as _recursive_repr

    class _Link(object):
        __slots__ = 'prev', 'next', 'key', '__weakref__'

    class OrderedDict(dict):
        'Dictionary that remembers insertion order'
        # An inherited dict maps keys to values. The inherited dict provides
        # __getitem__, __len__, __contains__, and get. The remaining methods
        # are order-aware. Big-O running times for all methods are the same as
        # regular dictionaries.

        # The internal self.__map dict maps keys to links in a doubly linked
        # list. The circular doubly linked list starts and ends with a sentinel
        # element. The sentinel element never gets deleted (this simplifies the
        # algorithm). The sentinel is in self.__hardroot with a weakref proxy
        # in self.__root. The prev links are weakref proxies (to prevent
        # circular references). Individual links are kept alive by the hard
        # reference in self.__map. Those hard references disappear when a key
        # is deleted from an OrderedDict.

        def __init__(self, *args, **kwds):
            '''Initialize an ordered dictionary.

            The signature is the same as regular dictionaries, but keyword
            arguments are not recommended because their insertion order is
            arbitrary.

            '''
            if len(args) > 1:
                raise TypeError('expected at most 1 arguments, got %d' %
                                len(args))
            try:
                self.__root
            except AttributeError:
                self.__hardroot = _Link()
                self.__root = root = _proxy(self.__hardroot)
                root.prev = root.next = root
                self.__map = {}
            self.__update(*args, **kwds)

        def __setitem__(self, key, value, dict_setitem=dict.__setitem__,
                        proxy=_proxy, Link=_Link):
            'od.__setitem__(i, y) <==> od[i]=y'
            # Setting a new item creates a new link at the end of the linked
            # list, and the inherited dictionary is updated with the new
            # key/value pair.
            if key not in self:
                self.__map[key] = link = Link()
                root = self.__root
                last = root.prev
                link.prev, link.next, link.key = last, root, key
                last.next = link
                root.prev = proxy(link)
            dict_setitem(self, key, value)

        def __delitem__(self, key, dict_delitem=dict.__delitem__):
            'od.__delitem__(y) <==> del od[y]'
            # Deleting an existing item uses self.__map to find the link which
            # gets removed by updating the links in the predecessor and
            # successor nodes.
            dict_delitem(self, key)
            link = self.__map.pop(key)
            link_prev = link.prev
            link_next = link.next
            link_prev.next = link_next
            link_next.prev = link_prev

        def __iter__(self):
            'od.__iter__() <==> iter(od)'
            # Traverse the linked list in order.
            root = self.__root
            curr = root.next
            while curr is not root:
                yield curr.key
                curr = curr.next

        def __reversed__(self):
            'od.__reversed__() <==> reversed(od)'
            # Traverse the linked list in reverse order.
            root = self.__root
            curr = root.prev
            while curr is not root:
                yield curr.key
                curr = curr.prev

        def clear(self):
            'od.clear() -> None.  Remove all items from od.'
            root = self.__root
            root.prev = root.next = root
            self.__map.clear()
            dict.clear(self)

        def popitem(self, last=True):
            '''od.popitem() -> (k, v), return and remove a (key, value) pair.

            Pairs are returned in LIFO order if last is true or FIFO order if
            false.

            '''
            if not self:
                raise KeyError('dictionary is empty')
            root = self.__root
            if last:
                link = root.prev
                link_prev = link.prev
                link_prev.next = root
                root.prev = link_prev
            else:
                link = root.next
                link_next = link.next
                root.next = link_next
                link_next.prev = root
            key = link.key
            del self.__map[key]
            value = dict.pop(self, key)
            return key, value

        def move_to_end(self, key, last=True):
            '''Move an existing element to the end (or beginning if
            ``last==False``).

            Raises KeyError if the element does not exist. When
            ``last==True``, acts like a fast version of
            ``self[key]=self.pop(key)``.

            '''
            link = self.__map[key]
            link_prev = link.prev
            link_next = link.next
            link_prev.next = link_next
            link_next.prev = link_prev
            root = self.__root
            if last:
                last = root.prev
                link.prev = last
                link.next = root
                last.next = root.prev = link
            else:
                first = root.next
                link.prev = root
                link.next = first
                root.next = first.prev = link

        def __sizeof__(self):
            sizeof = _sys.getsizeof
            n = len(self) + 1                      # links including root
            size = sizeof(self.__dict__)           # instance dictionary
            size += sizeof(self.__map) * 2         # internal & inherited dicts
            size += sizeof(self.__hardroot) * n    # link objects
            size += sizeof(self.__root) * n        # proxy objects
            return size

        update = __update = MutableMapping.update
        keys = MutableMapping.keys
        values = MutableMapping.values
        items = MutableMapping.items
        __ne__ = MutableMapping.__ne__

        __marker = object()    # TODO: Change for some UnsetType instance

        def pop(self, key, default=__marker):
            '''od.pop(k[,d]) -> v, remove specified key and return the
            corresponding value.

            If key is not found, d is returned if given, otherwise KeyError is
            raised.

            '''
            if key in self:
                result = self[key]
                del self[key]
                return result
            if default is self.__marker:
                raise KeyError(key)
            return default

        def setdefault(self, key, default=None):
            '''``od.setdefault(k[, d])`` -> ``od.get(k, d)`` also set
            ``od[k] = d if k not in od``'''
            if key in self:
                return self[key]
            self[key] = default
            return default

        @_recursive_repr()
        def __repr__(self):
            'od.__repr__() <==> repr(od)'
            if not self:
                return '%s()' % (self.__class__.__name__,)
            return '%s(%r)' % (self.__class__.__name__, list(self.items()))

        def __reduce__(self):
            'Return state information for pickling'
            items = [[k, self[k]] for k in self]
            inst_dict = vars(self).copy()
            for k in vars(OrderedDict()):
                inst_dict.pop(k, None)
            if inst_dict:
                return (self.__class__, (items,), inst_dict)
            return self.__class__, (items,)

        def copy(self):
            'od.copy() -> a shallow copy of od'
            return self.__class__(self)

        @classmethod
        def fromkeys(cls, iterable, value=None):
            '''``OD.fromkeys(S[, v])`` -> New ordered dictionary with keys from
            `S`. If not specified, the value defaults to None.

            '''
            self = cls()
            for key in iterable:
                self[key] = value
            return self

        def __eq__(self, other):
            '''``od.__eq__(y) <==> od==y``.  Comparison to another OD is
            order-sensitive while comparison to a regular mapping is
            order-insensitive.

            '''
            if isinstance(other, OrderedDict):
                return len(self) == len(other) and \
                    all(p == q for p, q in zip(self.items(), other.items()))
            return dict.__eq__(self, other)


if not _py34:
    class ChainMap(MutableMapping):
        '''A ChainMap groups multiple dicts (or other mappings) together
        to create a single, updateable view.

        The underlying mappings are stored in a list.  That list is public and
        can accessed or updated using the *maps* attribute.  There is no other
        state.

        Lookups search the underlying mappings successively until a key is
        found.  In contrast, writes, updates, and deletions only operate on
        the first mapping.

        '''

        def __init__(self, *maps):
            '''Initialize a ChainMap by setting *maps* to the given mappings.
            If no mappings are provided, a single empty dictionary is used.

            '''
            self.maps = list(maps) or [{}]    # always at least one map

        def __missing__(self, key):
            raise KeyError(key)

        def __getitem__(self, key):
            for mapping in self.maps:
                try:
                    return mapping[key]    # can't use 'key in mapping' with
                                           # defaultdict
                except KeyError:
                    pass
            return self.__missing__(key)    # support subclasses that define
                                            # __missing__

        def get(self, key, default=None):
            return self[key] if key in self else default

        def __len__(self):
            return len(set().union(*self.maps))  # reuses stored hash values
                                                 # if possible

        def __iter__(self):
            return iter(set().union(*self.maps))

        def __contains__(self, key):
            return any(key in m for m in self.maps)

        def __bool__(self):
            return any(self.maps)

        @_recursive_repr()
        def __repr__(self):
            return '{0.__class__.__name__}({1})'.format(
                self, ', '.join(map(repr, self.maps)))

        @classmethod
        def fromkeys(cls, iterable, *args):
            'Create a ChainMap with a single dict created from the iterable.'
            return cls(dict.fromkeys(iterable, *args))

        def copy(self):
            '''New ChainMap or subclass with a new copy of ``maps[0]`` and
            refs to ``maps[1:]``

            '''
            return self.__class__(self.maps[0].copy(), *self.maps[1:])

        __copy__ = copy

        def new_child(self, m=None):
            '''New ChainMap with a new map followed by all previous maps.

            If no map is provided, an empty dict is used.

            '''
            if m is None:
                m = {}
            return self.__class__(m, *self.maps)

        @property
        def parents(self):
            'New ChainMap from ``maps[1:]``.'
            return self.__class__(*self.maps[1:])

        def __setitem__(self, key, value):
            self.maps[0][key] = value

        def __delitem__(self, key):
            try:
                del self.maps[0][key]
            except KeyError:
                msg = 'Key not found in the first mapping: {!r}'.format(key)
                raise KeyError(msg)

        def popitem(self):
            '''Remove and return an item pair from ``maps[0]``.

            Raise KeyError is ``maps[0]`` is empty.

            '''
            try:
                return self.maps[0].popitem()
            except KeyError:
                raise KeyError('No keys found in the first mapping.')

        def pop(self, key, *args):
            '''Remove *key* from ``maps[0]`` and return its value.

            Raise KeyError if *key* not in ``maps[0]``.'''
            try:
                return self.maps[0].pop(key, *args)
            except KeyError:
                msg = 'Key not found in the first mapping: {!r}'.format(key)
                raise KeyError(msg)

        def clear(self):
            'Clear ``maps[0]``, leaving ``maps[1:]`` intact.'
            self.maps[0].clear()


if not _py33:
    class UserDict(MutableMapping):
        # Start by filling-out the abstract methods
        def __init__(self, dict=None, **kwargs):
            self.data = {}
            if dict is not None:
                self.update(dict)
            if len(kwargs):
                self.update(kwargs)

        def __len__(self):
            return len(self.data)

        def __getitem__(self, key):
            if key in self.data:
                return self.data[key]
            if hasattr(self.__class__, "__missing__"):
                return self.__class__.__missing__(self, key)
            raise KeyError(key)

        def __setitem__(self, key, item):
            self.data[key] = item

        def __delitem__(self, key):
            del self.data[key]

        def __iter__(self):
            return iter(self.data)

        # Modify __contains__ to work correctly when __missing__ is present
        def __contains__(self, key):
            return key in self.data

        # Now, add the methods in dicts but not in MutableMapping
        def __repr__(self):
            return repr(self.data)

        def copy(self):
            if self.__class__ is UserDict:
                return UserDict(self.data.copy())
            import copy
            data = self.data
            try:
                self.data = {}
                c = copy.copy(self)
            finally:
                self.data = data
            c.update(self)
            return c

        @classmethod
        def fromkeys(cls, iterable, value=None):
            d = cls()
            for key in iterable:
                d[key] = value
            return d

    class UserList(MutableSequence):
        """A more or less complete user-defined wrapper around list objects."""
        def __init__(self, initlist=None):
            self.data = []
            if initlist is not None:
                # XXX should this accept an arbitrary sequence?
                if type(initlist) == type(self.data):
                    self.data[:] = initlist
                elif isinstance(initlist, UserList):
                    self.data[:] = initlist.data[:]
                else:
                    self.data = list(initlist)

        def __repr__(self):
            return repr(self.data)

        def __lt__(self, other):
            return self.data < self.__cast(other)

        def __le__(self, other):
            return self.data <= self.__cast(other)

        def __eq__(self, other):
            return self.data == self.__cast(other)

        def __ne__(self, other):
            return self.data != self.__cast(other)

        def __gt__(self, other):
            return self.data > self.__cast(other)

        def __ge__(self, other):
            return self.data >= self.__cast(other)

        def __cast(self, other):
            return other.data if isinstance(other, UserList) else other

        def __contains__(self, item):
            return item in self.data

        def __len__(self):
            return len(self.data)

        def __getitem__(self, i):
            return self.data[i]

        def __setitem__(self, i, item):
            self.data[i] = item

        def __delitem__(self, i):
            del self.data[i]

        def __add__(self, other):
            if isinstance(other, UserList):
                return self.__class__(self.data + other.data)
            elif isinstance(other, type(self.data)):
                return self.__class__(self.data + other)
            return self.__class__(self.data + list(other))

        def __radd__(self, other):
            if isinstance(other, UserList):
                return self.__class__(other.data + self.data)
            elif isinstance(other, type(self.data)):
                return self.__class__(other + self.data)
            return self.__class__(list(other) + self.data)

        def __iadd__(self, other):
            if isinstance(other, UserList):
                self.data += other.data
            elif isinstance(other, type(self.data)):
                self.data += other
            else:
                self.data += list(other)
            return self

        def __mul__(self, n):
            return self.__class__(self.data*n)

        __rmul__ = __mul__

        def __imul__(self, n):
            self.data *= n
            return self

        def append(self, item):
            self.data.append(item)

        def insert(self, i, item):
            self.data.insert(i, item)

        def pop(self, i=-1):
            return self.data.pop(i)

        def remove(self, item):
            self.data.remove(item)

        def clear(self):
            self.data.clear()

        def copy(self):
            return self.__class__(self)

        def count(self, item):
            return self.data.count(item)

        def index(self, item, *args):
            return self.data.index(item, *args)

        def reverse(self):
            self.data.reverse()

        def sort(self, *args, **kwds):
            self.data.sort(*args, **kwds)

        def extend(self, other):
            if isinstance(other, UserList):
                self.data.extend(other.data)
            else:
                self.data.extend(other)

    class UserString(Sequence):
        def __init__(self, seq):
            if isinstance(seq, str):
                self.data = seq
            elif isinstance(seq, UserString):
                self.data = seq.data[:]
            else:
                self.data = str(seq)

        def __str__(self):
            return str(self.data)

        def __repr__(self):
            return repr(self.data)

        def __int__(self):
            return int(self.data)

        def __float__(self):
            return float(self.data)

        def __complex__(self):
            return complex(self.data)

        def __hash__(self):
            return hash(self.data)

        def __eq__(self, string):
            if isinstance(string, UserString):
                return self.data == string.data
            return self.data == string

        def __ne__(self, string):
            if isinstance(string, UserString):
                return self.data != string.data
            return self.data != string

        def __lt__(self, string):
            if isinstance(string, UserString):
                return self.data < string.data
            return self.data < string

        def __le__(self, string):
            if isinstance(string, UserString):
                return self.data <= string.data
            return self.data <= string

        def __gt__(self, string):
            if isinstance(string, UserString):
                return self.data > string.data
            return self.data > string

        def __ge__(self, string):
            if isinstance(string, UserString):
                return self.data >= string.data
            return self.data >= string

        def __contains__(self, char):
            if isinstance(char, UserString):
                char = char.data
            return char in self.data

        def __len__(self):
            return len(self.data)

        def __getitem__(self, index):
            return self.__class__(self.data[index])

        def __add__(self, other):
            if isinstance(other, UserString):
                return self.__class__(self.data + other.data)
            elif isinstance(other, str):
                return self.__class__(self.data + other)
            return self.__class__(self.data + str(other))

        def __radd__(self, other):
            if isinstance(other, str):
                return self.__class__(other + self.data)
            return self.__class__(str(other) + self.data)

        def __mul__(self, n):
            return self.__class__(self.data*n)

        __rmul__ = __mul__

        def __mod__(self, args):
            return self.__class__(self.data % args)

        # the following methods are defined in alphabetical order:
        def capitalize(self):
            return self.__class__(self.data.capitalize())

        def center(self, width, *args):
            return self.__class__(self.data.center(width, *args))

        def count(self, sub, start=0, end=_sys.maxsize):
            if isinstance(sub, UserString):
                sub = sub.data
            return self.data.count(sub, start, end)

        def encode(self, encoding=None, errors=None):  # XXX improve this?
            if encoding:
                if errors:
                    return self.__class__(self.data.encode(encoding, errors))
                return self.__class__(self.data.encode(encoding))
            return self.__class__(self.data.encode())

        def endswith(self, suffix, start=0, end=_sys.maxsize):
            return self.data.endswith(suffix, start, end)

        def expandtabs(self, tabsize=8):
            return self.__class__(self.data.expandtabs(tabsize))

        def find(self, sub, start=0, end=_sys.maxsize):
            if isinstance(sub, UserString):
                sub = sub.data
            return self.data.find(sub, start, end)

        def format(self, *args, **kwds):
            return self.data.format(*args, **kwds)

        def index(self, sub, start=0, end=_sys.maxsize):
            return self.data.index(sub, start, end)

        def isalpha(self):
            return self.data.isalpha()

        def isalnum(self):
            return self.data.isalnum()

        def isdecimal(self):
            return self.data.isdecimal()

        def isdigit(self):
            return self.data.isdigit()

        def isidentifier(self):
            return self.data.isidentifier()

        def islower(self):
            return self.data.islower()

        def isnumeric(self):
            return self.data.isnumeric()

        def isspace(self):
            return self.data.isspace()

        def istitle(self):
            return self.data.istitle()

        def isupper(self):
            return self.data.isupper()

        def join(self, seq):
            return self.data.join(seq)

        def ljust(self, width, *args):
            return self.__class__(self.data.ljust(width, *args))

        def lower(self):
            return self.__class__(self.data.lower())

        def lstrip(self, chars=None):
            return self.__class__(self.data.lstrip(chars))

        def partition(self, sep):
            return self.data.partition(sep)

        def replace(self, old, new, maxsplit=-1):
            if isinstance(old, UserString):
                old = old.data
            if isinstance(new, UserString):
                new = new.data
            return self.__class__(self.data.replace(old, new, maxsplit))

        def rfind(self, sub, start=0, end=_sys.maxsize):
            if isinstance(sub, UserString):
                sub = sub.data
            return self.data.rfind(sub, start, end)

        def rindex(self, sub, start=0, end=_sys.maxsize):
            return self.data.rindex(sub, start, end)

        def rjust(self, width, *args):
            return self.__class__(self.data.rjust(width, *args))

        def rpartition(self, sep):
            return self.data.rpartition(sep)

        def rstrip(self, chars=None):
            return self.__class__(self.data.rstrip(chars))

        def split(self, sep=None, maxsplit=-1):
            return self.data.split(sep, maxsplit)

        def rsplit(self, sep=None, maxsplit=-1):
            return self.data.rsplit(sep, maxsplit)

        def splitlines(self, keepends=False):
            return self.data.splitlines(keepends)

        def startswith(self, prefix, start=0, end=_sys.maxsize):
            return self.data.startswith(prefix, start, end)

        def strip(self, chars=None):
            return self.__class__(self.data.strip(chars))

        def swapcase(self):
            return self.__class__(self.data.swapcase())

        def title(self):
            return self.__class__(self.data.title())

        def translate(self, *args):
            return self.__class__(self.data.translate(*args))

        def upper(self):
            return self.__class__(self.data.upper())

        def zfill(self, width):
            return self.__class__(self.data.zfill(width))

    def _count_elements(mapping, iterable):
        self_get = mapping.get
        for elem in iterable:
            mapping[elem] = self_get(elem, 0) + 1

    class Counter(dict):
        '''Dict subclass for counting hashable items.  Sometimes called a bag
        or multiset.  Elements are stored as dictionary keys and their counts
        are stored as dictionary values.

        >>> c = Counter('abcdeabcdabcaba')  # count elements from a string

        >>> c.most_common(3)                # three most common elements
        [('a', 5), ('b', 4), ('c', 3)]
        >>> sorted(c)                       # list all unique elements
        ['a', 'b', 'c', 'd', 'e']
        >>> ''.join(sorted(c.elements()))   # list elements with repetitions
        'aaaaabbbbcccdde'
        >>> sum(c.values())            # total of all counts
        15

        >>> c['a']                     # count of letter 'a'
        5
        >>> for elem in 'shazam':      # update counts from an iterable
        ...     c[elem] += 1           # by adding 1 to each element's count
        >>> c['a']                     # now there are seven 'a'
        7
        >>> del c['b']                 # remove all 'b'
        >>> c['b']                     # now there are zero 'b'
        0

        >>> d = Counter('simsalabim')  # make another counter
        >>> c.update(d)                # add in the second counter
        >>> c['a']                     # now there are nine 'a'
        9

        >>> c.clear()                  # empty the counter
        >>> c
        Counter()

        Note:  If a count is set to zero or reduced to zero, it will remain
        in the counter until the entry is deleted or the counter is cleared:

        >>> c = Counter('aaabbc')
        >>> c['b'] -= 2               # reduce the count of 'b' by two
        >>> c.most_common()           # 'b' is still in, but its count is zero
        [('a', 3), ('c', 1), ('b', 0)]

        '''
        # References:
        # http://en.wikipedia.org/wiki/Multiset
        # http://www.gnu.org/software/smalltalk/manual-base/html_node/Bag.html
        # http://www.demo2s.com/Tutorial/Cpp/0380__set-multiset/Catalog0380__set-multiset.htm
        # http://code.activestate.com/recipes/259174/
        # Knuth, TAOCP Vol. II section 4.6.3

        def __init__(self, iterable=None, **kwds):
            '''Create a new, empty Counter object.  And if given, count
            elements from an input iterable.  Or, initialize the count from
            another mapping of elements to their counts.

            >>> c = Counter()                 # a new, empty counter
            >>> c = Counter('gallahad')       # a new counter from an iterable
            >>> c = Counter({'a': 4, 'b': 2})  # a new counter from a mapping
            >>> c = Counter(a=4, b=2)        # a new counter from keyword args

            '''
            super(Counter, self).__init__()
            self.update(iterable, **kwds)

        def __missing__(self, key):
            'The count of elements not in the Counter is zero.'
            # Needed so that self[missing_item] does not raise KeyError
            return 0

        def most_common(self, n=None):
            '''List the n most common elements and their counts from the most
            common to the least.  If n is None, then list all element counts.

            >>> Counter('abcdeabcdabcaba').most_common(3)
            [('a', 5), ('b', 4), ('c', 3)]

            '''
            # Emulate Bag.sortedByCount from Smalltalk
            if n is None:
                return sorted(self.items(), key=_itemgetter(1), reverse=True)
            return _heapq.nlargest(n, self.items(), key=_itemgetter(1))

        def elements(self):
            '''Iterator over elements repeating each as many times as its
            count.

            >>> c = Counter('ABCABC')
            >>> sorted(c.elements())
            ['A', 'A', 'B', 'B', 'C', 'C']

            # Knuth's example for prime factors of 1836:  2**2 * 3**3 * 17**1
            >>> prime_factors = Counter({2: 2, 3: 3, 17: 1})
            >>> product = 1
            >>> for factor in prime_factors.elements():     # loop over factors
            ...     product *= factor                       # and multiply them
            >>> product
            1836

            Note, if an element's count has been set to zero or is a negative
            number, elements() will ignore it.

            '''
            # Emulate Bag.do from Smalltalk and Multiset.begin from C++.
            return _chain.from_iterable(_starmap(_repeat, self.items()))

        # Override dict methods where necessary

        @classmethod
        def fromkeys(cls, iterable, v=None):
            # There is no equivalent method for counters because setting v=1
            # means that no element can have a count greater than one.
            raise NotImplementedError('Counter.fromkeys() is undefined.  '
                                      'Use Counter(iterable) instead.')

        def update(self, iterable=None, **kwds):
            '''Like dict.update() but add counts instead of replacing them.

            Source can be an iterable, a dictionary, or another Counter
            instance.

            >>> c = Counter('which')
            >>> c.update('witch')       # add elements from another iterable
            >>> d = Counter('watch')
            >>> c.update(d)             # add elements from another counter
            >>> c['h']                  # four 'h' in which, witch, and watch
            4

            '''
            # The regular dict.update() operation makes no sense here because
            # the replace behavior results in the some of original untouched
            # counts being mixed-in with all of the other counts for a mismash
            # that doesn't have a straight-forward interpretation in most
            # counting contexts.  Instead, we implement straight-addition.
            # Both the inputs and outputs are allowed to contain zero and
            # negative counts.

            if iterable is not None:
                if isinstance(iterable, Mapping):
                    if self:
                        self_get = self.get
                        for elem, count in iterable.items():
                            self[elem] = count + self_get(elem, 0)
                    else:
                        # fast path when counter is empty
                        super(Counter, self).update(iterable)
                else:
                    _count_elements(self, iterable)
            if kwds:
                self.update(kwds)

        def subtract(self, iterable=None, **kwds):
            '''Like dict.update() but subtracts counts instead of replacing
            them.

            Counts can be reduced below zero.  Both the inputs and outputs are
            allowed to contain zero and negative counts.

            Source can be an iterable, a dictionary, or another Counter
            instance.

            Examples::

              >>> c = Counter('which')

            Subtract elements from another iterable::

              >>> c.subtract('witch')

            Subtract elements from another counter::

              >>> c.subtract(Counter('watch'))

            2 in which, minus 1 in witch, minus 1 in watch::

              >>> c['h']
              0

            1 in which, minus 1 in witch, minus 1 in watch::

              >>> c['w']
              -1

            '''
            if iterable is not None:
                self_get = self.get
                if isinstance(iterable, Mapping):
                    for elem, count in iterable.items():
                        self[elem] = self_get(elem, 0) - count
                else:
                    for elem in iterable:
                        self[elem] = self_get(elem, 0) - 1
            if kwds:
                self.subtract(kwds)

        def copy(self):
            'Return a shallow copy.'
            return self.__class__(self)

        def __reduce__(self):
            return self.__class__, (dict(self),)

        def __delitem__(self, elem):
            '''Like dict.__delitem__() but does not raise KeyError for missing
            values.'''
            if elem in self:
                super(Counter, self).__delitem__(elem)

        def __repr__(self):
            if not self:
                return '%s()' % self.__class__.__name__
            try:
                items = ', '.join(map('%r: %r'.__mod__, self.most_common()))
                return '%s({%s})' % (self.__class__.__name__, items)
            except TypeError:
                # handle case where values are not orderable
                return '{0}({1!r})'.format(self.__class__.__name__, dict(self))

        # Multiset-style mathematical operations discussed in:
        #       Knuth TAOCP Volume II section 4.6.3 exercise 19
        #       and at http://en.wikipedia.org/wiki/Multiset
        #
        # Outputs guaranteed to only include positive counts.
        #
        # To strip negative and zero counts, add-in an empty counter:
        #       c += Counter()

        def __add__(self, other):
            '''Add counts from two counters.

            >>> Counter('abbb') + Counter('bcc')
            Counter({'b': 4, 'c': 2, 'a': 1})

            '''
            if not isinstance(other, Counter):
                return NotImplemented
            result = Counter()
            for elem, count in self.items():
                newcount = count + other[elem]
                if newcount > 0:
                    result[elem] = newcount
            for elem, count in other.items():
                if elem not in self and count > 0:
                    result[elem] = count
            return result

        def __sub__(self, other):
            ''' Subtract count, but keep only results with positive counts.

            >>> Counter('abbbc') - Counter('bccd')
            Counter({'b': 2, 'a': 1})

            '''
            if not isinstance(other, Counter):
                return NotImplemented
            result = Counter()
            for elem, count in self.items():
                newcount = count - other[elem]
                if newcount > 0:
                    result[elem] = newcount
            for elem, count in other.items():
                if elem not in self and count < 0:
                    result[elem] = 0 - count
            return result

        def __or__(self, other):
            '''Union is the maximum of value in either of the input counters.

            >>> Counter('abbb') | Counter('bcc')
            Counter({'b': 3, 'c': 2, 'a': 1})

            '''
            if not isinstance(other, Counter):
                return NotImplemented
            result = Counter()
            for elem, count in self.items():
                other_count = other[elem]
                newcount = other_count if count < other_count else count
                if newcount > 0:
                    result[elem] = newcount
            for elem, count in other.items():
                if elem not in self and count > 0:
                    result[elem] = count
            return result

        def __and__(self, other):
            ''' Intersection is the minimum of corresponding counts.

            >>> Counter('abbb') & Counter('bcc')
            Counter({'b': 1})

            '''
            if not isinstance(other, Counter):
                return NotImplemented
            result = Counter()
            for elem, count in self.items():
                other_count = other[elem]
                newcount = count if count < other_count else other_count
                if newcount > 0:
                    result[elem] = newcount
            return result

        def __pos__(self):
            '''Adds an empty counter, effectively stripping negative and zero
            counts.'''
            return self + Counter()

        def __neg__(self):
            '''Subtracts from an empty counter.  Strips positive and zero
            counts, and flips the sign on negative counts.

            '''
            return Counter() - self

        def _keep_positive(self):
            '''Internal method to strip elements with a negative or zero
            count.'''
            nonpositive = [elem for elem, count in self.items()
                           if not count > 0]
            for elem in nonpositive:
                del self[elem]
            return self

        def __iadd__(self, other):
            '''Inplace add from another counter, keeping only positive counts.

            >>> c = Counter('abbb')
            >>> c += Counter('bcc')
            >>> c
            Counter({'b': 4, 'c': 2, 'a': 1})

            '''
            for elem, count in other.items():
                self[elem] += count
            return self._keep_positive()

        def __isub__(self, other):
            '''Inplace subtract counter, but keep only results with positive
            counts.

            >>> c = Counter('abbbc')
            >>> c -= Counter('bccd')
            >>> c
            Counter({'b': 2, 'a': 1})

            '''
            for elem, count in other.items():
                self[elem] -= count
            return self._keep_positive()

        def __ior__(self, other):
            '''Inplace union is the maximum of value from either counter.

            >>> c = Counter('abbb')
            >>> c |= Counter('bcc')
            >>> c
            Counter({'b': 3, 'c': 2, 'a': 1})

            '''
            for elem, other_count in other.items():
                count = self[elem]
                if other_count > count:
                    self[elem] = other_count
            return self._keep_positive()

        def __iand__(self, other):
            '''Inplace intersection is the minimum of corresponding counts.

            >>> c = Counter('abbb')
            >>> c &= Counter('bcc')
            >>> c
            Counter({'b': 1})

            '''
            for elem, count in self.items():
                other_count = other[elem]
                if other_count < count:
                    self[elem] = other_count
            return self._keep_positive()

### ;; end of Python 3.3 backport


class StackedDict(OpenDictMixin, SmartDictMixin, MutableMapping):
    '''A multi-level mapping.

    A level is entered by using the :meth:`push` and is leaved by calling
    :meth:`pop`.

    The property :attr:`level` returns the actual number of levels.

    When accessing keys they are searched from the lastest level "upwards", if
    such a key does not exists in any level a KeyError is raised.

    Deleting a key only works in the *current level*; if it's not defined there
    a KeyError is raised. This means that you can't delete keys from the upper
    levels without :func:`popping <pop>`.

    Setting the value for key, sets it in the current level.

    .. versionchanged:: 1.5.2 Based on the newly introduced :class:`ChainMap`.

    '''
    __slots__ = (safe.slot('inner', ChainMap),
                 safe.slot(OpenDictMixin.__cache_name__, dict))

    def __init__(self, *args, **kwargs):
        # Each data item is stored as {key: {level: value, ...}}
        self.update(*args, **kwargs)

    @property
    def level(self):
        '''Return the current level number.

        The first level is 0.  Calling :meth:`push` increases the current
        level (and returns it), while calling :meth:`pop` decreases the
        current level (if possible).

        '''
        return len(self.inner.maps) - 1

    def push(self, *args, **kwargs):
        '''Pushes a whole new level to the stacked dict.

        :param args: Several mappings from which the new level will be
                     initialled filled.

        :param kwargs: Values to fill the new level.

        :returns: The pushed :attr:`level` number.

        '''
        self.inner = self.inner.new_child()
        self.update(*args, **kwargs)
        return self.level

    def pop(self):
        '''Pops the last pushed level and returns the whole level.

        If there are no levels in the stacked dict, a TypeError is raised.

        :returns:  A dict containing the poped level.

        '''
        if self.level > 0:
            stack = self.inner
            res = stack.maps[0]
            self.inner = stack.parents
            return res
        else:
            raise TypeError('Cannot pop from StackedDict without any levels')

    def peek(self):
        '''Peeks the top level of the stack.

        Returns a copy of the top-most level without any of the keys from
        lower levels.

        Example::

           >>> sdict = StackedDict(a=1, b=2)
           >>> sdict.push(c=3)  # it returns the level...
           1
           >>> sdict.peek()
           {'c': 3}

        '''
        return dict(self.inner.maps[0])

    def __str__(self):
        # TODO: Optimize
        return str(dict(self))

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, str(self))

    def __len__(self):
        return len(self.inner)

    def __iter__(self):
        return iter(self.inner)

    def __getitem__(self, key):
        return self.inner[key]

    def __setitem__(self, key, value):
        self.inner[key] = value

    def __delitem__(self, key):
        del self.inner[key]


class OrderedSmartDict(SmartDictMixin, OrderedDict):
    '''A combination of the the OrderedDict with the
    :class:`SmartDictMixin`.

    .. warning:: Initializing with kwargs does not ensure any initial ordering,
                 since Python's keyword dict is not ordered. Use a list/tuple
                 of pairs instead.

    '''
    def __init__(self, *args, **kwds):
        '''Initialize an ordered dictionary.

        The signature is the same as regular dictionaries, but keyword
        arguments are not recommended because their insertion order is
        arbitrary.

        '''
        super(OrderedSmartDict, self).__init__()
        self.update(*args, **kwds)

# get rid of unused global variables
del slist, _py33, _py34
