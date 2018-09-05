#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Extensions to Python's ``collections`` module.

You may use it as drop-in replacement of ``collections``. Although we don't
document all items here. Refer to `collections <collections>`:mod:
documentation.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from collections import *    # noqa
try:
    from collections.abc import *  # noqa
    from collections.abc import (
        Set,
        Iterable,
        Sized,
        Container,
        MutableSet,
        Mapping,
        MutableMapping
    )
except ImportError:
    from collections import (
        Set,
        Iterable,
        Sized,
        Container,
        MutableSet,
        Mapping,
        MutableMapping
    )


import collections as _stdlib    # noqa
from collections import (_itemgetter, _heapq, _chain, _repeat, _starmap)

try:
    from collection import _sys    # noqa
except ImportError:
    import sys as _sys

from xoutil.deprecation import deprecated    # noqa
from xoutil.eight import python_version    # noqa
from xoutil.symbols import Unset    # noqa
from xoutil.objects import SafeDataItem as safe    # noqa
from xoutil.reprlib import recursive_repr    # noqa

if python_version == 2:
    # Fix some sub-classing problems.
    from xoutil.future.types import MappingProxyType    # noqa
    del MappingProxyType    # already fixed there
    MutableSequence.register(deque)    # noqa


class safe_dict_iter(tuple):
    '''Iterate a dictionary in a safe way.

    This is useful when a dictionary can be modified while iterating on it,
    for example::

      >>> d = {1: 2, 3: 4, 5: 6}
      >>> di = safe_dict_iter(d)

      >>> for k, v in di.items():
      ...     d[v] = k

      >>> [(k, v) for (k, v) in di.items()]
      [(1, 2), (3, 4), (5, 6)]

      >>> del d[1]

      >>> [(k, v) for (k, v) in di.items()]
      [(3, 4), (5, 6)]

      >>> [k for k in di]
      [3, 5]

    '''

    def __new__(cls, mapping):
        self = super().__new__(cls, mapping)
        self._mapping = mapping
        return self

    def __str__(self):
        cls_name = type(self).__name__
        res = str(', ').join(str(i) for i in self)
        return str('{}({})').format(cls_name, res)
    __repr__ = __str__

    def __len__(self):
        return sum(1 for key in self)

    def __contains__(self, key):
        res = super().__contains__(key)
        return res and key in self.mapping

    def __nonzero__(self):
        return bool(len(self))
    __bool__ = __nonzero__

    def __iter__(self):
        for key in super().__iter__():
            if key in self._mapping:
                yield key
    keys = __iter__

    def values(self):
        for key in self:
            if key in self._mapping:
                yield self._mapping[key]

    def items(self):
        for key in self:
            if key in self._mapping:
                yield (key, self._mapping[key])


class defaultdict(_stdlib.defaultdict):
    '''A hack for ``collections.defaultdict`` that passes the key and a copy of
    self as a plain dict (to avoid infinity recursion) to the callable.

    Examples::

        >>> from xoutil.future.collections import defaultdict
        >>> d = defaultdict(lambda key, d: 'a')
        >>> d['abc']
        'a'

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
                return super().__missing__(key)
        else:
            raise KeyError(key)


class OpenDictMixin:
    '''A mixin for mappings implementation that expose keys as attributes.

    For example:

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

    ``_key2identifier``

        Protected method, receives a key as argument and must return a valid
        identifier that is used instead the key as an extended attribute.

    ``__cache_name__``

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

    Classes or Mixins that can be integrated with `dict` by inheritance must
    not have a `__slots__` definition.  Because of that, this mixin must not
    declare any slot.  If needed, it must be declared explicitly in customized
    classed like in the example in the first part of this documentation or in
    the definition of `opendict` class.

    '''
    __cache_name__ = str('_inverted_cache')

    def __dir__(self):
        '''Return normal "dir" plus valid keys as attributes.'''
        # TODO: Check if super must be called if defined
        from xoutil.objects import fulldir
        return list(set(~self) | fulldir(self))

    def __getattr__(self, name):
        from xoutil.future.inspect import get_attr_value
        _mark = object()
        res = get_attr_value(self, name, _mark)
        if res is not _mark:
            return res
        else:
            key = (~self).get(name)
            if key:
                return self[key]
            else:
                msg = "'%s' object has no attribute '%s'"
                raise AttributeError(msg % (type(self).__name__, name))

    def __setattr__(self, name, value):
        cls = type(self)
        desc = getattr(cls, name, None)
        if desc is not None:    # Prioritize descriptors
            try:
                desc.__set__(self, value)
            except Exception:
                pass
        key = (~self).get(name)
        if key:
            self[key] = value
        else:
            super().__setattr__(name, value)

    def __delattr__(self, name):
        key = (~self).get(name)
        if key:
            del self[key]
        else:
            super().__delattr__(name)

    def __invert__(self):
        '''Return an inverted mapping between key and attribute names.

        Keys of the resulting dictionary are identifiers for attribute names
        and values are original key names.

        Class attribute "__separators__" are used to calculate it and is
        cached in '_inverted_cache slot safe variable.

        Several keys could have the same identifier, only one will be valid and
        used.

        To obtain this mapping you can use as the unary operator "~".

        '''
        KEY_LENGTH = 'length'
        KEY_MAPPING = 'mapping'
        cache = self._cache
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

    @property
    def _cache(self):
        from xoutil.future.inspect import get_attr_value
        try:
            return get_attr_value(self, type(self).__cache_name__)
        except AttributeError:
            res = setattr(self, type(self).__cache_name__, dict())
            return res

    @staticmethod
    def _key2identifier(key):
        '''Convert keys to valid identifiers.

        This method could be redefined in sub-classes to change this feature.
        This function must return a valid identifier or None if the conversion
        is not possible.

        '''
        # TODO: Improve this in order to obtain a full-mapping.  For example,
        # the corresponding attribute names for the keys ``'-x-y'`` and
        # ``'x-y'`` are the same, in that case only one will be returning.
        from xoutil.keywords import suffix_kwd
        from xoutil.string import slugify
        from xoutil.validators import is_valid_identifier
        res = key if is_valid_identifier(key) else slugify(key, '_')
        return suffix_kwd(res)


class SmartDictMixin:
    '''A mixin that extends the `update` method of dictionaries

    Standard method allow only one positional argument, this allow several.

    Note on using mixins in Python: method resolution order is calculated in
    the order of inheritance, if a mixin is defined to overwrite behavior
    already existent, use first that classes with it. See `SmartDict`:class:
    below.

    '''
    def update(*args, **kwds):
        '''Update this dict from a set of iterables `args` and keyword values
        `kwargs`.

        Each positional argument could be:

        - another mapping (any object implementing "keys" and
          `~object.__getitem__`:meth: methods.

        - an iterable of (key, value) pairs.

        '''
        from xoutil.params import issue_9137
        self, args = issue_9137(args)
        for key, value in smart_iter_items(*args, **kwds):
            self[key] = value

    # TODO: Include new argument ``full=True`` to also search in string
    #       values.  Maybe this kind of feature will be better in a function
    #       instead a method.
    def search(self, pattern):
        '''Return new mapping with items which key match a `pattern` regexp.

        This function always tries to return a valid new mapping of the same
        type of the caller instance.  If the constructor of corresponding type
        can't be called without arguments, then look up for a class
        variable named `__search_result_type__` or return a standard
        Python dictionary if not found.

        '''
        from re import compile
        regexp = compile(pattern)
        cls = type(self)
        try:
            res = cls()
        except Exception:
            from xoutil.future.inspect import get_attr_value
            creator = get_attr_value(cls, '__search_result_type__', None)
            res = creator() if creator else {}
        for key in self:
            if regexp.search(key):
                res[key] = self[key]
        return res


class SmartDict(SmartDictMixin, dict):
    '''A "smart" dictionary that can receive a wide variety of arguments.

    See `SmartDictMixin.update`:meth: and :meth:`SmartDictMixin.search`.

    '''
    def __init__(*args, **kwargs):
        from xoutil.params import issue_9137
        self, args = issue_9137(args)
        super().__init__()
        self.update(*args, **kwargs)


class opendict(OpenDictMixin, dict):
    '''A dictionary implementation that mirrors its keys as attributes.

    For example::

      >>> d = opendict(es='spanish')
      >>> d.es
      'spanish'

      >>> d['es'] = 'espanol'
      >>> d.es
      'espanol'

    Setting attributes not already included  *does not* makes them keys::

      >>> d.en = 'English'
      >>> set(d)
      {'es'}

    '''
    __slots__ = safe.slot(OpenDictMixin.__cache_name__, dict)

    @classmethod
    def from_enum(cls, enumclass):
        '''Creates an opendict from an enumeration class.

        If `enumclass` lacks the ``__members__`` dictionary, take the
        ``__dict__`` of the class disregarding the keys that cannot be `public
        identifiers
        <xoutil.validators.identifiers.is_valid_public_identifier>`:func:.  If
        `enumclass` has the ``__members__`` attribute this is the same as
        ``opendict(enumclass.__members__)``.

        Example:

        .. code-block:: python

           >>> from xoutil.future.collections import opendict
           >>> @opendict.from_enum
           >>> class Foo(object):
           ...    x = 1
           ...    _y = 2

           >>> type(Foo) is opendict
           True

           >>> dict(Foo)
           {'x': 1}

        '''
        from xoutil.symbols import Unset
        from xoutil.validators.identifiers import is_valid_public_identifier
        members = getattr(enumclass, '__members__', Unset)
        if members is Unset:
            members = {
                k: v
                for k, v in enumclass.__dict__.items()
                if is_valid_public_identifier(k)
            }
        return cls(members)


class codedict(OpenDictMixin, dict):
    '''A dictionary implementation that evaluate keys as Python expressions.

    This is also a open dict (see `OpenDictMixin`:class: for more info).

    Example:

      >>> cd = codedict(x=1, y=2, z=3.0)
      >>> '{_[x + y]} is 3 --  {_[x + z]} is 4.0'.format(_=cd)
      '3 is 3 --  4.0 is 4.0'

    It supports the right shift (``>>``) operator as a format operand (using
    ``_`` as the special name for the code dict):

      >>> cd >> '{_[x + y]} is 3 --  {_[x + z]} is 4.0 -- {x} is 1'
      '3 is 3 --  4.0 is 4.0 -- 1 is 1'

    It also implements the left shift (``<<``) operator:

      >>> '{_[x + y]} is 3 --  {_[x + z]} is 4.0 -- {x} is 1' << cd
      '3 is 3 --  4.0 is 4.0 -- 1 is 1'

    .. versionadded:: 1.8.3

    '''
    def __getitem__(self, key):
        from xoutil.eight import string_types
        try:
            return super().__getitem__(key)
        except KeyError:
            if isinstance(key, string_types):
                return eval(key, dict(self))
            else:
                raise

    def __rshift__(self, arg):
        return arg.format(_=self, **self)

    __rlshift__ = __rshift__


try:
    from collections import _count_elements
except ImportError:
    def _count_elements(mapping, iterable):
        'Tally elements from the iterable.'
        mapping_get = mapping.get
        for elem in iterable:
            mapping[elem] = mapping_get(elem, 0) + 1


if python_version < 3.3:
    class UserDict(MutableMapping):
        # Start by filling-out the abstract methods
        def __init__(*args, **kwargs):
            from xoutil.params import issue_9137
            self, args = issue_9137(args)
            self.data = {}
            self.update(*args, **kwargs)

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

    class UserList(_stdlib.MutableSequence):
        '''A more or less complete user-defined wrapper around lists.'''
        def __init__(self, initlist=None):
            if initlist is not None:
                if type(initlist) is list:
                    self.data = initlist[:]
                elif isinstance(initlist, UserList):
                    self.data = initlist.data[:]
                else:
                    self.data = list(initlist)
            else:
                self.data = []

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
            return self.__class__(self.data * n)

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

    class UserString(_stdlib.Sequence):
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
            return self.__class__(self.data * n)

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

        def __init__(*args, **kwds):
            '''Create a new, empty Counter object.  And if given, count
            elements from an input iterable.  Or, initialize the count from
            another mapping of elements to their counts.

            >>> c = Counter()                 # a new, empty counter
            >>> c = Counter('gallahad')       # a new counter from an iterable
            >>> c = Counter({'a': 4, 'b': 2})  # a new counter from a mapping
            >>> c = Counter(a=4, b=2)        # a new counter from keyword args

            '''
            from xoutil.params import issue_9137
            self, args = issue_9137(args)
            self.data = {}
            super().__init__()
            self.update(*args, **kwds)

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

        def update(*args, **kwds):
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
            from xoutil.params import issue_9137, check_count
            self, args = issue_9137(args)
            check_count(args, 0, 1, caller='update')
            if args:
                iterable = args[0]
                if isinstance(iterable, Mapping):
                    if self:
                        self_get = self.get
                        for elem, count in iterable.items():
                            self[elem] = count + self_get(elem, 0)
                    else:
                        # fast path when counter is empty
                        super().update(iterable)
                else:
                    _count_elements(self, iterable)
            if kwds:
                self.update(kwds)

        def subtract(*args, **kwds):
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
            from xoutil.params import issue_9137, check_count
            self, args = issue_9137(args)
            check_count(args, 0, 1, caller='subtract')
            if args:
                iterable = args[0]
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
                super().__delitem__(elem)

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

# ;; end of Python 3.3 backport


class StackedDict(OpenDictMixin, SmartDictMixin, MutableMapping):
    '''A multi-level mapping.

    A level is entered by using the `push`:meth: and is leaved by calling
    `pop`:meth:.

    The property `level`:attr: returns the actual number of levels.

    When accessing keys they are searched from the latest level "upwards", if
    such a key does not exists in any level a KeyError is raised.

    Deleting a key only works in the *current level*; if it's not defined there
    a KeyError is raised. This means that you can't delete keys from the upper
    levels without `popping <pop>`:func:.

    Setting the value for key, sets it in the current level.

    .. versionchanged:: 1.5.2 Based on the newly introduced `ChainMap`:class:.

    '''
    __slots__ = (safe.slot('inner', ChainMap),
                 safe.slot(OpenDictMixin.__cache_name__, dict))

    def __init__(*args, **kwargs):
        # Each data item is stored as {key: {level: value, ...}}
        from xoutil.params import issue_9137
        self, args = issue_9137(args)
        self.update(*args, **kwargs)

    @property
    def level(self):
        '''Return the current level number.

        The first level is 0.  Calling `push`:meth: increases the current
        level (and returns it), while calling `pop`:meth: decreases the
        current level (if possible).

        '''
        return len(self.inner.maps) - 1

    def push_level(self, *args, **kwargs):
        '''Pushes a whole new level to the stacked dict.

        :param args: Several mappings from which the new level will be
                     initialled filled.

        :param kwargs: Values to fill the new level.

        :returns: The pushed `level`:attr: number.

        '''
        self.inner = self.inner.new_child()
        self.update(*args, **kwargs)
        return self.level

    @deprecated(push_level)
    def push(self, *args, **kwargs):
        '''Don't use thid method, use new `push_level`:meth: instead.'''
        return self.push_level(*args, **kwargs)

    def pop(self, *args):
        '''Remove this, always use original `MutableMapping.pop`:meth:.

        If none arguments are given, `pop_level`:meth: is called and a
        deprecation warning is printed in `sys.stderr` the first time.  If one
        or two arguments are given, those are interpreted as (key, default)
        values of the super class `pop`:meth:.

        '''
        if len(args) == 0:
            cls = type(self)
            if not hasattr(cls, '_bad_pop_called'):
                import warnings
                setattr(cls, '_bad_pop_called', True)
                msg = ('Use `pop` method without parameters is deprecated, '
                       'use `pop_level` instead')
                warnings.warn(msg, stacklevel=2)
            return self.pop_level()
        else:
            return super().pop(*args)

    def pop_level(self):
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


class RankedDict(SmartDictMixin, dict):
    '''Mapping that remembers modification order.

    Differences with `OrderedDict`:class: are:

    - Can be ranked (change precedence order) at any time; see `rank`:meth:
      and `swap_ranks`:meth: methods for more information.

    - Based in modification, not in insertion order.

    - Keeps the standard semantics of Python for `popitem`:meth: method
      returning a random pair when called without parameters.

    '''

    def __init__(*args, **kwds):
        '''Initialize a ranked dictionary.

        The signature is the same as regular dictionaries, but keyword
        arguments are not recommended because their insertion order is
        arbitrary.

        Use `rank`:meth: to change the precedence order in any moment.

        '''
        from xoutil.params import issue_9137
        self, args = issue_9137(args)
        # Ensure direct calls to ``__init__`` don't clear previous contents
        try:
            self._ranks
        except AttributeError:
            self._ranks = []
        self.update(*args, **kwds)

    def rank(self, *keys):
        '''Arrange mapping keys into a systematic precedence order.

        :param keys: Variable number of key values, given are ordered in the
               highest precedence levels (0 is the most priority).  Not given
               keys are added at the end in the its current order.

        '''
        if keys:
            ranks = []
            for key in keys:
                if key in self:
                    ranks.append(key)
                else:
                    raise KeyError('{}'.format(key))
            aux = set(keys)
            for key in self:
                if key not in aux:
                    ranks.append(key)
            self._ranks = ranks

    def swap_ranks(self, *args, **kwds):
        '''Exchange ranks of given keys.

        :param args: Each item must be a pair of keys to exchange the order of
               precedence.

        :param kwds: Every keyword argument will have a pair to exchange
               (name, value).

        '''
        from xoutil.params import check_count
        check_count(len(args) + len(kwds) + 1, 2, caller='swap_ranks')
        for key1, key2 in args:
            self._swap_ranks(key1, key2)
        for key1 in kwds:
            key2 = kwds[key1]
            self._swap_ranks(key1, key2)

    def move_to_end(self, key, last=True):
        '''Move an existing element to the end.

        Or move it to the beginning if ``last==False``.

        Raises KeyError if the element does not exist.  When ``last==True``,
        acts like a fast version of ``self[key] = self.pop(key)``.

        .. note:: This method is kept for compatibility with
                  `OrderedDict`:class:\ .  Last example using
                  ``self.pop(key)`` works well in both, in OD and this class,
                  but here in `RankedDict`:class: it's semantically equivalent
                  to ``self[key] = self[key]``.

        '''
        try:
            ranks = self._ranks
            if last:
                if key != ranks[-1]:
                    ranks.remove(key)
                    ranks.append(key)
            else:
                if key != ranks[0]:
                    ranks.remove(key)
                    ranks.insert(0, key)
        except ValueError:
            raise KeyError(key)

    def _swap_ranks(self, key1, key2):
        '''Protected method to swap a pair of ranks.'''
        if key1 in self and key2 in self:
            ranks = self._ranks
            idx1, idx2 = ranks.index(key1), ranks.index(key2)
            if idx1 != idx2:
                aux = ranks[idx1]
                ranks[idx1] = ranks[idx2]
                ranks[idx2] = aux
        else:
            raise KeyError('{!r} and/or {!r}'.format(key1, key2))

    def __setitem__(self, key, value):
        '''rd.__setitem__(i, y) <==> rd[i]=y'''
        ranks = self._ranks
        if key in self:
            if ranks[-1] != key:
                ranks.remove(key)
                ranks.append(key)
        else:
            ranks.append(key)
        super().__setitem__(key, value)

    def __delitem__(self, key):
        '''rd.__delitem__(y) <==> del rd[y]'''
        super().__delitem__(key)
        self._ranks.remove(key)

    def __iter__(self):
        '''rd.__iter__() <==> iter(rd)'''
        return iter(self._ranks)

    def __reversed__(self):
        '''rd.__reversed__() <==> reversed(rd)'''
        return reversed(self._ranks)

    def clear(self):
        '''rd.clear() -> None.  Remove all items from rd.'''
        super().clear()
        self._ranks = []

    def popitem(self, index=None):
        '''rd.popitem([index]) -> (key, value), return and remove a pair.

        :param index: Position of pair to return (default last).  This method
               isn't have the same semantic as in `OrderedDict`:class: one,
               none the defined in method with the same name in standard
               Python mappings; here is similar to `~list.pop`:meth:.

        '''
        if self:
            if index is None or index is True:
                index = -1
            key = self._ranks.pop(index)
            return key, super().pop(key)
        else:
            raise KeyError('popitem(): dictionary is empty')

    def __sizeof__(self):
        '''D.__sizeof__() -> size of D in memory, in bytes.

        .. note:: Why ``sys.getsizeof(obj)`` doesn't return the same result as
                  ``obj.__sizeof__()``?

        '''
        return super().__sizeof__() + self._ranks.__sizeof__()

    def keys(self):
        '''D.keys() -> an object providing a view on D's keys.'''
        return self.__iter__()

    def values(self):
        '''D.values() -> an object providing a view on D's values.'''
        for key in self:
            yield self[key]

    def items(self):
        '''D.items() -> an object providing a view on D's items.'''
        for key in self:
            yield (key, self[key])

    if python_version == 2:
        iterkeys = keys
        itervalues = values
        iteritems = items

    def __eq__(self, other):
        '''rd.__eq__(y) <==> rd==y.

        Comparison to another `RankedDict`:class: instance is order-sensitive
        while comparison to a regular mapping is order-insensitive.

        '''
        res = super().__eq__(other)
        if res:
            if isinstance(other, RankedDict):
                return self._ranks == other._ranks
            elif isinstance(other, OrderedDict):
                return self._ranks == list(other)
            else:
                return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def pop(self, key, *args):
        '''rd.pop(k[,d]) -> v

        Remove specified key and return the corresponding value.

        If key is not found, d is returned if given, otherwise KeyError is
        raised.

        '''
        from xoutil.params import check_count
        count = len(args)
        check_count(count + 1, 1, 2, caller='pop')
        res = super().pop(key, Unset)
        if res is Unset:
            if count == 1:
                return args[0]
            else:
                raise KeyError(key)
        else:
            self._ranks.remove(key)
            return res

    def setdefault(self, key, default=None):
        '''D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D'''
        if key in self:
            return self[key]
        else:
            self[key] = default
            return default

    @recursive_repr()
    def __repr__(self):
        '''x.__repr__() <==> repr(x)'''
        aux = ', '.join('({!r}, {!r})'.format(k, self[k]) for k in self)
        if aux:
            aux = '[{}]'.format(aux)
        return '{}({})'.format(type(self).__name__, aux)

    def __reduce__(self):
        '''Return state information for pickling.'''
        cls = type(self)
        inst_dict = vars(self).copy()
        for k in vars(cls()):
            inst_dict.pop(k, None)
        return cls, (), inst_dict or None, None, iter(self.items())

    def copy(self):
        '''D.copy() -> a shallow copy of D.'''
        return type(self)(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        '''RD.fromkeys(S[, v]) -> New ranked dictionary with keys from S.

        If not specified, the value defaults to None.

        '''
        return cls((key, value) for key in iterable)


class OrderedSmartDict(SmartDictMixin, OrderedDict):
    '''A combination of the `OrderedDict` with the `SmartDictMixin`.

    .. warning:: Initializing with kwargs does not ensure any initial ordering,
                 since Python's keyword dict is not ordered. Use a list/tuple
                 of pairs instead.

    '''
    def __init__(*args, **kwds):
        '''Initialize an ordered dictionary.

        The signature is the same as regular dictionaries, but keyword
        arguments are not recommended because their insertion order is
        arbitrary.

        '''
        from xoutil.params import issue_9137
        self, args = issue_9137(args)
        super().__init__()
        self.update(*args, **kwds)


class MetaSet(type):
    '''Allow syntax sugar creating sets.

    This is pythonic syntax (stop limit is never included), for example::

        >>> from xoutil.future.collections import PascalSet as srange
        >>> [i for i in srange[1:4, 15, 20:23]]
        [1, 2, 3, 15, 20, 21, 22, 23]

    '''
    def __getitem__(cls, ranges):
        return cls(*ranges) if isinstance(ranges, tuple) else cls(ranges)


class PascalSet(metaclass=MetaSet):
    '''Collection of unique integer elements (implemented with intervals).

    ::

       PascalSet(*others) -> new set object

    .. versionadded:: 1.7.1

    '''
    __slots__ = ('_items',)

    def __init__(self, *others):
        '''Initialize self.

        :param others: Any number of integer or collection of integers that
               will be the set members.

        '''
        self._items = []    # a list of list of two elements
        self.update(*others)

    def __str__(self):
        from xoutil.eight import range

        def aux(s, e):
            if s == e:
                return str(s)
            elif s + 1 == e:
                return '%s, %s' % (s, e)
            else:
                return '%s..%s' % (s, e)

        l = self._items
        ranges = ((l[i], l[i + 1]) for i in range(0, len(l), 2))
        return str('{%s}' % ', '.join((aux(s, e) for (s, e) in ranges)))

    def __repr__(self):
        cls = type(self)
        cname = cls.__name__
        return str('%s([%s])' % (cname, ', '.join((str(i) for i in self))))

    def __iter__(self):
        l = self._items
        i, count = 0, len(l)
        while i < count:
            s, e = l[i], l[i + 1]
            while s <= e:
                yield s
                s += 1
            i += 2

    def __len__(self):
        res = 0
        l = self._items
        i, count = 0, len(l)
        while i < count:
            res += l[i + 1] - l[i] + 1
            i += 2
        return res

    def __nonzero__(self):
        return bool(self._items)
    __bool__ = __nonzero__

    def __contains__(self, other):
        '''True if set has an element ``other``, else False.'''
        from xoutil.eight import integer_types
        return isinstance(other, integer_types) and self._search(other)[0]

    def __hash__(self):
        '''Compute the hash value of a set.'''
        return Set._hash(self)

    if python_version == 2:
        def __cmp__(self, other):
            # Python 3 automatically generate a TypeError when no mechanism is
            # found by returning `NotImplemented` special value.  In Python 2
            # this patch method must be generated
            from xoutil.eight import type_name
            sname = type_name(self)
            oname = type_name(other)
            msg = 'unorderable types: "%s" and "%s"!'
            raise TypeError(msg % (sname, oname))

    def __eq__(self, other):
        '''Python 2 and 3 have several differences in operator definitions.

        For example::

          >>> from xoutil.future.collections import PascalSet
          >>> s1 = PascalSet[0:10]
          >>> assert s1 == set(s1)    # OK (True) in 2 and 3
          >>> assert set(s1) == s1    # OK in 3, fails in 2

        '''
        if isinstance(other, Set):
            ls, lo = len(self), len(other)
            if ls == lo:
                if isinstance(other, PascalSet):
                    return self._items == other._items
                else:
                    return self.count(other) == ls
            else:
                return False
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if isinstance(other, Set):
            if other:
                return self.issuperset(other) and len(self) > len(other)
            else:
                return bool(self._items)
        else:
            return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Set):
            if other:
                return self.issuperset(other)
            else:
                return bool(self._items)
        else:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Set):
            if other:
                return self.issubset(other) and len(self) < len(other)
            else:
                return not self._items
        else:
            return NotImplemented

    def __le__(self, other):
        if isinstance(other, Set):
            if other:
                return self.issubset(other)
            else:
                return not self._items
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Set):
            return self.difference(other)
        else:
            return NotImplemented

    def __isub__(self, other):
        if isinstance(other, Set):
            self.difference_update(other)
            return self
        else:
            return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, Set):
            return other - type(other)(self)
        else:
            return NotImplemented

    def __and__(self, other):
        if isinstance(other, Set):
            return self.intersection(other)
        else:
            return NotImplemented

    def __iand__(self, other):
        if isinstance(other, Set):
            self.intersection_update(other)
            return self
        else:
            return NotImplemented

    def __rand__(self, other):
        if isinstance(other, Set):
            return other & type(other)(self)
        else:
            return NotImplemented

    def __or__(self, other):
        if isinstance(other, Set):
            return self.union(other)
        else:
            return NotImplemented

    def __ior__(self, other):
        if isinstance(other, Set):
            self.update(other)
            return self
        else:
            return NotImplemented

    def __ror__(self, other):
        if isinstance(other, Set):
            return other | type(other)(self)
        else:
            return NotImplemented

    def __xor__(self, other):
        if isinstance(other, Set):
            return self.symmetric_difference(other)
        else:
            return NotImplemented

    def __ixor__(self, other):
        if isinstance(other, Set):
            self.symmetric_difference_update(other)
            return self
        else:
            return NotImplemented

    def __rxor__(self, other):
        if isinstance(other, Set):
            return other ^ type(other)(self)
        else:
            return NotImplemented

    def count(self, other):
        '''Number of occurrences of any member of other in this set.

        If other is an integer, return 1 if present, 0 if not.

        '''
        from xoutil.eight import integer_types
        if isinstance(other, integer_types):
            return 1 if other in self else 0
        else:
            return sum((i in self for i in other), 0)

    def add(self, other):
        '''Add an element to a set.

        This has no effect if the element is already present.

        '''
        self._insert(other)

    def union(self, *others):
        '''Return the union of sets as a new set.

        (i.e. all elements that are in either set.)

        '''
        res = self.copy()
        res.update(*others)
        return res

    def update(self, *others):
        '''Update a set with the union of itself and others.'''
        from xoutil.eight import integer_types, range
        for other in others:
            if isinstance(other, PascalSet):
                l = other._items
                if self._items:
                    count = len(l)
                    i = 0
                    while i < count:
                        self._insert(l[i], l[i + 1])
                        i += 2
                else:
                    self._items = l[:]
            elif isinstance(other, integer_types):
                self._insert(other)
            elif isinstance(other, Iterable):
                for i in other:
                    self._insert(i)
            elif isinstance(other, slice):
                start, stop, step = other.start, other.stop, other.step
                if step is None:
                    step = 1
                if step in (1, -1):
                    stop -= step
                    if step == -1:
                        start, stop = stop, start
                    self._insert(start, stop)
                else:
                    for i in range(start, stop, step):
                        self._insert(i)
            else:
                raise self._invalid_value(other)

    def intersection(self, *others):
        '''Return the intersection of two or more sets as a new set.

        (i.e. elements that are common to all of the sets.)

        '''
        res = self.copy()
        res.intersection_update(*others)
        return res

    def intersection_update(self, *others):
        '''Update a set with the intersection of itself and another.'''
        from xoutil.eight import integer_types as ints
        l = self._items
        oi, count = 0, len(others)
        while l and oi < count:
            other = others[oi]
            if not isinstance(other, PascalSet):
                # safe mode for intersection
                other = PascalSet(i for i in other if isinstance(i, ints))
            o = other._items
            if o:
                sl, el = l[0], l[-1]
                so, eo = o[0], o[-1]
                if sl < so:
                    self._remove(sl, so - 1)
                if eo < el:
                    self._remove(eo + 1, el)
                i = 2
                while l and i < len(o):
                    s, e = o[i - 1] + 1, o[i] - 1
                    if s <= e:
                        self._remove(s, e)
                    i += 2
            else:
                del l[:]
            oi += 1

    def difference(self, *others):
        '''Return the difference of two or more sets as a new set.

        (i.e. all elements that are in this set but not the others.)

        '''
        res = self.copy()
        res.difference_update(*others)
        return res

    def difference_update(self, *others):
        '''Remove all elements of another set from this set.'''
        for other in others:
            if isinstance(other, PascalSet):
                l = other._items
                count = len(l)
                i = 0
                while i < count:
                    self._remove(l[i], l[i + 1])
                    i += 2
            else:
                from xoutil.eight import integer_types
                for i in other:
                    if isinstance(i, integer_types):
                        self._remove(i)

    def symmetric_difference(self, other):
        '''Return the symmetric difference of two sets as a new set.

        (i.e. all elements that are in exactly one of the sets.)

        '''
        res = self.copy()
        res.symmetric_difference_update(other)
        return res

    def symmetric_difference_update(self, other):
        'Update a set with the symmetric difference of itself and another.'
        if not isinstance(other, PascalSet):
            other = PascalSet(other)
        if self:
            if other:
                # TODO: Implement more efficiently
                aux = other - self
                self -= other
                self |= aux
        else:
            self._items = other._items[:]

    def discard(self, other):
        '''Remove an element from a set if it is a member.

        If the element is not a member, do nothing.

        '''
        self._remove(other)

    def remove(self, other):
        '''Remove an element from a set; it must be a member.

        If the element is not a member, raise a KeyError.

        '''
        if other in self:
            self._remove(other)
        else:
            raise KeyError('"%s" is not a member!' % other)

    def pop(self):
        '''Remove and return an arbitrary set element.

        Raises KeyError if the set is empty.

        '''
        l = self._items
        if l:
            res = l[0]
            if l[0] < l[1]:
                l[0] += 1
            else:
                del l[0:2]
            return res
        else:
            raise KeyError('pop from an empty set!')

    def clear(self):
        '''Remove all elements from this set.'''
        self._items = []

    def copy(self):
        '''Return a shallow copy of a set.'''
        return type(self)(self)

    def isdisjoint(self, other):
        '''Return True if two sets have a null intersection.'''
        if isinstance(other, PascalSet):
            if self and other:
                l, o = self._items, other._items
                i, lcount, ocount = 0, len(l), len(o)
                maybe = True
                while maybe and i < lcount:
                    found, idx = other._search(l[i])
                    if idx == ocount:    # exhausted
                        # assert not found
                        i = lcount
                    elif found or l[i + 1] >= o[idx]:
                        maybe = False
                    else:
                        i += 2
                return maybe
            else:
                return True
        else:
            return not any(i in self for i in other)

    def issubset(self, other):
        '''Report whether another set contains this set.'''
        ls = len(self)
        if isinstance(other, PascalSet):
            if self:
                if ls > len(other):  # Fast check for obvious cases
                    return False
                else:
                    l, o = self._items, other._items
                    i, lcount = 0, len(l)
                    maybe = True
                    while maybe and i < lcount:
                        found, idx = other._search(l[i])
                        if found and l[i + 1] <= o[idx + 1]:
                            i += 2
                        else:
                            maybe = False
                    return maybe
            else:
                return True
        elif isinstance(other, Sized) and ls > len(other):
            # Fast check for obvious cases
            return False
        elif isinstance(other, Container):
            aux = next((i for i in self if i not in other), Unset)
            return aux is Unset
        else:
            # Generator cases
            from operator import add
            from functools import reduce
            lo = reduce(add, (i in self for i in other), 0)
            return lo == ls

    def issuperset(self, other):
        '''Report whether this set contains another set.'''
        ls = len(self)
        if isinstance(other, PascalSet):
            if other:
                if ls < len(other):  # Fast check for obvious cases
                    return False
                else:
                    l, o = self._items, other._items
                    i, ocount = 0, len(o)
                    maybe = True
                    while maybe and i < ocount:
                        found, idx = self._search(o[i])
                        if found and o[i + 1] <= l[idx + 1]:
                            i += 2
                        else:
                            maybe = False
                    return maybe
            else:
                return True
        elif isinstance(other, Sized) and ls < len(other):
            # Fast check for obvious cases
            return False
        else:
            aux = next((i for i in other if i not in self), Unset)
            return aux is Unset

    def _search(self, other):
        '''Search the pair where ``other`` is placed.

        Return a duple :``(if found or not, index)``.

        '''
        from xoutil.eight import integer_types
        if isinstance(other, integer_types):
            l = self._items
            start, end = 0, len(l)
            res, pivot = False, 2 * (end // 4)
            while not res and start < end:
                s, e = l[pivot], l[pivot + 1]
                if other < s:
                    end = pivot
                elif other > e:
                    start = pivot + 2
                else:
                    res = True
                pivot = start + 2 * ((end - start) // 4)
            return res, pivot
        else:
            raise self._invalid_value(other)

    def _insert(self, start, end=None):
        '''Insert an interval of integers.'''
        if not end:
            end = start
        assert start <= end
        l = self._items
        count = len(l)
        found, idx = self._search(start)
        if not found:
            if idx > 0 and start == l[idx - 1] + 1:
                found = True
                idx -= 2
                l[idx + 1] = start
                if idx < count - 2 and end == l[idx + 2] - 1:
                    end = l[idx + 3]
            elif idx < count and end >= l[idx] - 1:
                found = True
                l[idx] = start
        if found:
            while end > l[idx + 1]:
                if idx < count - 2 and end >= l[idx + 2] - 1:
                    if end <= l[idx + 3]:
                        l[idx + 1] = l[idx + 3]
                    del l[idx + 2:idx + 4]
                    count -= 2
                else:
                    l[idx + 1] = end
        else:
            if idx < count:
                l.insert(idx, start)
                l.insert(idx + 1, end)
            else:
                l.extend((start, end))
            count += 2

    def _remove(self, start, end=None):
        '''Remove an interval of integers.'''
        if not end:
            end = start
        assert start <= end
        l = self._items
        sfound, sidx = self._search(start)
        efound, eidx = self._search(end)
        if sfound and efound and sidx == eidx:
            first = l[sidx] < start
            last = l[eidx + 1] > end
            if first and last:
                l.insert(eidx + 1, end + 1)
                l.insert(sidx + 1, start - 1)
            elif first:
                l[sidx + 1] = start - 1
            elif last:
                l[eidx] = end + 1
            else:
                del l[sidx:eidx + 2]
        else:
            if sfound and l[sidx] < start:
                l[sidx + 1] = start - 1
                sidx += 2
            if efound:
                if l[eidx + 1] > end:
                    l[eidx] = end + 1
                else:
                    eidx += 2
            if sidx < eidx:
                del l[sidx:eidx]

    def _invalid_value(self, value):
        from xoutil.eight import type_name
        cls_name = type_name(self)
        vname = type_name(value)
        msg = ('Unsupported type for  value "%s" of type "%s" for a "%s", '
               'must be an integer!')
        return TypeError(msg % (value, vname, cls_name))

    @classmethod
    def _prime_numbers_until(cls, limit):
        '''This is totally a funny test method.'''
        from xoutil.eight import range
        res = cls[2:limit]
        for i in range(2, limit // 2 + 1):
            if i in res:
                aux = i + i
                while aux < limit:
                    if aux in res:
                        res.remove(aux)
                    aux += i
        return res


MutableSet.register(PascalSet)


class BitPascalSet(metaclass=MetaSet):
    '''Collection of unique integer elements (implemented with bit-wise sets).

    ::

        BitPascalSet(*others) -> new bit-set object

    .. versionadded:: 1.7.1

    '''
    __slots__ = ('_items',)
    _bit_length = 62    # How many values are stored in each item

    def __init__(self, *others):
        '''Initialize self.

        :param others: Any number of integer or collection of integers that
               will be the set members.

        In this case `_items` is a dictionary with keys containing number
        division seeds and values bit-wise integers (each bit is the division
        modulus position).

        '''
        self._items = {}
        self.update(*others)

    def __str__(self):
        if self:
            return str(PascalSet(self))
        else:
            cname = type(self).__name__
            return str('%s([])') % cname

    def __repr__(self):
        cname = type(self).__name__
        res = str(', ').join(str(i) for i in self)
        return str('%s([%s])') % (cname, res)

    def __iter__(self):
        bl = self._bit_length
        sm = self._items
        for k in sorted(sm):
            v = sm[k]
            base = k * bl
            i = 0
            ref = 1
            while i < bl:
                if ref & v:
                    yield base + i
                ref <<= 1
                i += 1

    def __len__(self):
        return sum((1 for i in self), 0)

    def __nonzero__(self):
        return bool(self._items)
    __bool__ = __nonzero__

    def __contains__(self, other):
        '''True if this bit-set has the element ``other``, else False.'''
        res = self._search(other)
        if res:
            k, ref, v = res
            return bool(v & (1 << ref))
        else:
            return False

    def __hash__(self):
        '''Compute the hash value of a set.'''
        return Set._hash(self)

    if python_version == 2:
        def __cmp__(self, other):
            # Python 3 automatically generate a TypeError when no mechanism is
            # found by returning `NotImplemented` special value.  In Python 2
            # this patch method must be generated
            from xoutil.eight import type_name
            sname = type_name(self)
            oname = type_name(other)
            msg = 'unorderable types: "%s" and "%s"!'
            raise TypeError(msg % (sname, oname))

    def __eq__(self, other):
        '''Python 2 and 3 have several differences in operator definitions.

        For example::

          >>> from xoutil.future.collections import BitPascalSet
          >>> s1 = BitPascalSet[0:10]
          >>> assert s1 == set(s1)    # OK (True) in 2 and 3
          >>> assert set(s1) == s1    # OK in 3, fails in 2

        '''
        if isinstance(other, Set):
            if isinstance(other, BitPascalSet):
                return self._items == other._items
            else:
                ls, lo = len(self), len(other)
                return ls == lo == self.count(other)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if isinstance(other, Set):
            if other:
                return self.issuperset(other) and len(self) > len(other)
            else:
                return bool(self._items)
        else:
            return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Set):
            return self.issuperset(other) if other else bool(self._items)
        else:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Set):
            if other:
                return self.issubset(other) and len(self) < len(other)
            else:
                return not self._items
        else:
            return NotImplemented

    def __le__(self, other):
        if isinstance(other, Set):
            return self.issubset(other) if other else not self._items
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Set):
            return self.difference(other)
        else:
            return NotImplemented

    def __isub__(self, other):
        if isinstance(other, Set):
            self.difference_update(other)
            return self
        else:
            return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, Set):
            return other - type(other)(self)
        else:
            return NotImplemented

    def __and__(self, other):
        if isinstance(other, Set):
            return self.intersection(other)
        else:
            return NotImplemented

    def __iand__(self, other):
        if isinstance(other, Set):
            self.intersection_update(other)
            return self
        else:
            return NotImplemented

    def __rand__(self, other):
        if isinstance(other, Set):
            return other & type(other)(self)
        else:
            return NotImplemented

    def __or__(self, other):
        if isinstance(other, Set):
            return self.union(other)
        else:
            return NotImplemented

    def __ior__(self, other):
        if isinstance(other, Set):
            self.update(other)
            return self
        else:
            return NotImplemented

    def __ror__(self, other):
        if isinstance(other, Set):
            return other | type(other)(self)
        else:
            return NotImplemented

    def __xor__(self, other):
        if isinstance(other, Set):
            return self.symmetric_difference(other)
        else:
            return NotImplemented

    def __ixor__(self, other):
        if isinstance(other, Set):
            self.symmetric_difference_update(other)
            return self
        else:
            return NotImplemented

    def __rxor__(self, other):
        if isinstance(other, Set):
            return other ^ type(other)(self)
        else:
            return NotImplemented

    def count(self, other):
        '''Number of occurrences of any member of other in this set.

        If other is an integer, return 1 if present, 0 if not.

        '''
        from xoutil.eight import integer_types
        if isinstance(other, integer_types):
            return 1 if other in self else 0
        else:
            return sum((i in self for i in other), 0)

    def add(self, other):
        '''Add an element to a bit-set.

        This has no effect if the element is already present.

        '''
        self._insert(other)

    def union(self, *others):
        '''Return the union of bit-sets as a new set.

        (i.e. all elements that are in either set.)

        '''
        res = self.copy()
        res.update(*others)
        return res

    def update(self, *others):
        '''Update a bit-set with the union of itself and others.'''
        from xoutil.eight import integer_types, range
        for other in others:
            if isinstance(other, BitPascalSet):
                sm = self._items
                om = other._items
                for k, v in safe_dict_iter(om).items():
                    if k in sm:
                        sm[k] |= v
                    else:
                        sm[k] = v
            elif isinstance(other, integer_types):
                self._insert(other)
            elif isinstance(other, Iterable):
                for i in other:
                    self._insert(i)
            elif isinstance(other, slice):
                start, stop, step = other.start, other.stop, other.step
                if step is None:
                    step = 1
                for i in range(start, stop, step):
                    self._insert(i)
            else:
                raise self._invalid_value(other)

    def intersection(self, *others):
        '''Return the intersection of two or more bit-sets as a new set.

        (i.e. elements that are common to all of the sets.)

        '''
        res = self.copy()
        res.intersection_update(*others)
        return res

    def intersection_update(self, *others):
        '''Update a bit-set with the intersection of itself and another.'''
        from xoutil.eight import integer_types as ints
        sm = self._items
        oi, count = 0, len(others)
        while sm and oi < count:
            other = others[oi]
            if not isinstance(other, BitPascalSet):
                # safe mode for intersection
                other = PascalSet(i for i in other if isinstance(i, ints))
            om = other._items
            for k, v in safe_dict_iter(sm).items():
                v &= om.get(k, 0)
                if v:
                    sm[k] = v
                else:
                    del sm[k]
            oi += 1

    def difference(self, *others):
        '''Return the difference of two or more bit-sets as a new set.

        (i.e. all elements that are in this set but not the others.)

        '''
        res = self.copy()
        res.difference_update(*others)
        return res

    def difference_update(self, *others):
        '''Remove all elements of another bit-set from this set.'''
        for other in others:
            if isinstance(other, BitPascalSet):
                sm = self._items
                om = other._items
                for k, v in safe_dict_iter(om).items():
                    if k in sm:
                        v = sm[k] & ~v
                        if v:
                            sm[k] = v
                        else:
                            del sm[k]
            else:
                from xoutil.eight import integer_types
                for i in other:
                    if isinstance(i, integer_types):
                        self._remove(i)

    def symmetric_difference(self, other):
        '''Return the symmetric difference of two bit-sets as a new set.

        (i.e. all elements that are in exactly one of the sets.)

        '''
        res = self.copy()
        res.symmetric_difference_update(other)
        return res

    def symmetric_difference_update(self, other):
        'Update a bit-set with the symmetric difference of itself and another.'
        if not isinstance(other, BitPascalSet):
            other = BitPascalSet(other)
        if self:
            if other:
                # TODO: Implement more efficiently
                aux = other - self
                self -= other
                self |= aux
        else:
            self._items = other._items[:]

    def discard(self, other):
        '''Remove an element from a bit-set if it is a member.

        If the element is not a member, do nothing.

        '''
        self._remove(other)

    def remove(self, other):
        '''Remove an element from a bit-set; it must be a member.

        If the element is not a member, raise a KeyError.

        '''
        self._remove(other, fail=True)

    def pop(self):
        '''Remove and return an arbitrary bit-set element.

        Raises KeyError if the set is empty.

        '''
        from xoutil.eight import iteritems
        sm = self._items
        if sm:
            bl = self._bit_length
            k, v = next(iteritems(sm))
            assert v
            base = k * bl
            i = 0
            ref = 1
            res = None
            while res is None:
                if ref & v:
                    res = base + i
                else:
                    ref <<= 1
                    i += 1
            v &= ~ref
            if v:
                sm[k] = v
            else:
                del sm[k]
            return res
        else:
            raise KeyError('pop from an empty set!')

    def clear(self):
        '''Remove all elements from this bit-set.'''
        self._items = {}

    def copy(self):
        '''Return a shallow copy of a set.'''
        return type(self)(self)

    def isdisjoint(self, other):
        '''Return True if two bit-sets have a null intersection.'''
        from xoutil.eight import iteritems
        if isinstance(other, BitPascalSet):
            sm, om = self._items, other._items
            if sm and om:
                return all(sm.get(k, 0) & v == 0 for k, v in iteritems(om))
            else:
                return True
        else:
            return not any(i in self for i in other)

    def issubset(self, other):
        '''Report whether another set contains this bit-set.'''
        from xoutil.eight import iteritems
        if isinstance(other, BitPascalSet):
            sm, om = self._items, other._items
            if sm:
                return all(om.get(k, 0) & v == v for k, v in iteritems(sm))
            else:
                return True
        elif isinstance(other, Container):
            return not any(i not in other for i in self)
        else:
            # Generator cases
            return sum((i in self for i in other), 0) == len(self)

    def issuperset(self, other):
        '''Report whether this bit set contains another set.'''
        from xoutil.eight import iteritems
        if isinstance(other, BitPascalSet):
            sm, om = self._items, other._items
            if om:
                return all(sm.get(k, 0) & v == v for k, v in iteritems(om))
            else:
                return True
        else:
            return not any(i not in self for i in other)

    def _search(self, other):
        '''Search the bit-wise value where ``other`` could be placed.

        Return a duple :``(seed, bits to shift left)``.

        '''
        from xoutil.eight import integer_types
        if isinstance(other, integer_types):
            sm = self._items
            bl = self._bit_length
            k, ref = divmod(other, bl)
            return k, ref, sm.get(k, 0)
        else:
            return None

    def _insert(self, other):
        '''Add a member in this bit-set.'''
        aux = self._search(other)
        if aux:
            k, ref, v = aux
            self._items[k] = v | (1 << ref)
        else:
            raise self._invalid_value(other)

    def _remove(self, other, fail=False):
        '''Remove an interval of integers from this bit-set.'''
        aux = self._search(other)
        ok = False
        if aux:
            k, ref, v = aux
            if v:
                aux = v & ~(1 << ref)
                if v != aux:
                    ok = True
                    sm = self._items
                    if aux:
                        sm[k] = aux
                    else:
                        del sm[k]
        if not ok and fail:
            raise KeyError('"%s" is not a member!' % other)

    def _invalid_value(self, value):
        from xoutil.eight import type_name
        cls_name = type_name(self)
        vname = type_name(value)
        msg = ('Unsupported type for  value "%s" of type "%s" for a "%s", '
               'must be an integer!')
        return TypeError(msg % (value, vname, cls_name))

    @classmethod
    def _prime_numbers_until(cls, limit):
        '''This is totally a funny test method.'''
        from xoutil.eight import range
        res = cls[2:limit]
        for i in range(2, limit // 2 + 1):
            if i in res:
                aux = i + i
                while aux < limit:
                    if aux in res:
                        res.remove(aux)
                    aux += i
        return res


MutableSet.register(BitPascalSet)


# Smart Tools

def pair(arg):
    '''Check if `arg` is a pair (two elements tuple or list).'''
    return arg if isinstance(arg, (tuple, list)) and len(arg) == 2 else None


def smart_iter_items(*args, **kwds):
    '''Unify iteration over (key, value) pairs.

    If a pair of pairs is found, e.g. ``[(1, 2), (3, 4)]``, instead of
    yielding one pair (the outermost), inner two pairs takes precedence.

    '''
    for arg in args:
        if isinstance(arg, Mapping):
            for key in arg:
                yield key, arg[key]
        elif hasattr(arg, 'keys') and hasattr(arg, '__getitem__'):
            # Custom mappings
            for key in arg.keys():
                yield key, arg[key]
        elif pair(arg) and not (pair(arg[0]) and pair(arg[1])):
            yield arg
        else:
            for item in arg:
                if pair(item):
                    yield item
                else:
                    from xoutil.eight import type_name
                    msg = "'{}' object '{}' is not a pair"
                    raise TypeError(msg.format(type_name(item), item))
    for key in kwds:
        yield key, kwds[key]


# get rid of unused global variables
del deprecated, recursive_repr
