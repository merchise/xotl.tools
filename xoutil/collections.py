# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# xoutil.collections
# ----------------------------------------------------------------------
# Copyright 2013 Merchise Autrement and Contributors for the defaultdict and
# opendict implementations.
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
# @created: Jul 3, 2012
#
# Contributors from Medardo Rodríguez:
#    - Manuel Vázquez Acosta <manu@merchise.org>
#    - Medardo Rodriguez <med@merchise.org>


'''Extensions to Python's ``collections`` module.

You may use it as drop-in replacement of ``collections``. Although we don't
document all items here. Refer to :mod:`collections <py:collections>`
documentation.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)

from collections import *

from xoutil.compat import defaultdict as _defaultdict
from xoutil.compat import py32 as _py32


class defaultdict(_defaultdict):
    '''A hack for ``collections.defaultdict`` that passes the key and a copy of
    self as a plain dict (to avoid infinity recursion) to the callable.

    Examples::

        >>> from xoutil.default_dict import defaultdict
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


class opendict(dict):
    '''A dictionary implementation that mirrors its keys as attributes::

        >>> d = opendict({'es': 'spanish'})
        >>> d.es
        'spanish'

        >>> d['es'] = 'espanol'
        >>> d.es
        'espanol'

    '''
    def __getattr__(self, name):
        try:
            return super(opendict, self).__getattr__(name)
        except AttributeError:
            if name in self:
                return self[name]
            else:
                raise

if not _py32:
    # From this point below: Copyright (c) 2001-2013, Python Software
    # Foundation; All rights reserved.

    import sys as _sys
    from weakref import proxy as _proxy
    from xoutil.reprlib import recursive_repr as _recursive_repr

    _CacheInfo = namedtuple("CacheInfo", "hits misses maxsize currsize")

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
            '''Initialize an ordered dictionary. The signature is the same as regular
            dictionaries, but keyword arguments are not recommended because
            their insertion order is arbitrary.

            '''
            if len(args) > 1:
                raise TypeError('expected at most 1 arguments, got %d' % len(args))
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
            '''Move an existing element to the end (or beginning if last==False).

            Raises KeyError if the element does not exist.  When last=True, acts
            like a fast version of self[key]=self.pop(key).

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
            n = len(self) + 1                       # number of links including root
            size = sizeof(self.__dict__)            # instance dictionary
            size += sizeof(self.__map) * 2          # internal dict and inherited dict
            size += sizeof(self.__hardroot) * n     # link objects
            size += sizeof(self.__root) * n         # proxy objects
            return size

        update = __update = MutableMapping.update
        keys = MutableMapping.keys
        values = MutableMapping.values
        items = MutableMapping.items
        __ne__ = MutableMapping.__ne__

        __marker = object()

        def pop(self, key, default=__marker):
            '''od.pop(k[,d]) -> v, remove specified key and return the corresponding value.

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
            'od.setdefault(k[,d]) -> od.get(k,d), also set od[k]=d if k not in od'
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
            '''OD.fromkeys(S[, v]) -> New ordered dictionary with keys from S.  If not
            specified, the value defaults to None.

            '''
            self = cls()
            for key in iterable:
                self[key] = value
            return self

        def __eq__(self, other):
            '''od.__eq__(y) <==> od==y.  Comparison to another OD is order-sensitive while
            comparison to a regular mapping is order-insensitive.

            '''
            if isinstance(other, OrderedDict):
                return len(self) == len(other) and \
                       all(p == q for p, q in zip(self.items(), other.items()))
            return dict.__eq__(self, other)
