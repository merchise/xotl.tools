#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.iterators
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~] and Contributors
# Copyright (c) 2011, 2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Manuel Vázquez Acosta <mva.led@gmail.com>
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2011-11-08

'''Several util functions for iterators'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

from xoutil.symbols import Unset

from xoutil.deprecation import deprecated

# TODO: Evaluate rename to 'xoutil.future.itertools'.

def first_non_null(iterable, default=None):
    '''Returns the first value from iterable which is non-null.

    This is roughly the same as::

         next((x for x in iter(iterable) if x), default)

    .. versionadded:: 1.4.0
    '''
    return next((x for x in iter(iterable) if x), default)


def flatten(sequence, is_scalar=None, depth=None):
    '''Flatten-out a sequence.

    It takes care of everything deemed a collection (i.e, not a scalar
    according to the callable passed in `is_scalar` argument; if ``None``,
    `xoutil.types.is_scalar`:func: is assumed)::

        >>> from xoutil.eight import range
        >>> range_ = lambda *a: list(range(*a))
        >>> tuple(flatten((1, range_(2, 5), range(5, 10))))
        (1, 2, 3, 4, 5, 6, 7, 8, 9)

    If `depth` is None the collection is flattened recursiverly until the
    "bottom" is reached. If `depth` is an integer then the collection is
    flattened up to that level. `depth=0` means not to flatten. Nested
    iterators are not "exploded" if under the stated `depth`::

        # In the following doctest we use ``...range(...X)`` because the
        # string repr of range differs in Py2 and Py3k.

        >>> tuple(flatten((range_(2), range(2, 4)), depth=0))  # doctest: +ELLIPSIS
        ([0, 1], ...range(2, 4))

        >>> tuple(flatten((range(2), range_(2, 4)), depth=0))  # doctest: +ELLIPSIS
        (...range(...2), [2, 3])

    '''
    if is_scalar is None:
        from xoutil.types import is_scalar
    for item in sequence:
        if is_scalar(item):
            yield item
        elif depth == 0:
            yield item
        else:
            if depth is not None:
                depth = depth - 1
            for subitem in flatten(item, is_scalar, depth=depth):
                yield subitem


def pop_first(source, keys, default=None):
    '''Pop first value from `source` from given `keys`.

    :param source: Any compatible mapping.

    :param keys: Reference keys to pop the value.

    Examples::

      >>> d = {'x': 1, 'y': 2, 'z': 3}
      >>> pop_first(d, ('a', 'y', 'x'), '---')
      2

      >>> pop_first(d, ('a', 'y', 'x'), '---')
      1

      >>> pop_first(d, ('a', 'y', 'x'), '---')
      '---'

    '''
    return next((source.pop(key) for key in keys if key in source), default)


def multi_pop(source, *keys):
    '''Pop values from `source` of all given `keys`.

    :param source: Any compatible mapping.

    :param keys: Keys to pop values.

    All keys that are not found are ignored.

    Examples::

      >>> d = {'x': 1, 'y': 2, 'z': 3}
      >>> next(multi_pop(d, 'a', 'y', 'x'), '---')
      2

      >>> next(multi_pop(d, 'a', 'y', 'x'), '---')
      1

      >>> next(multi_pop(d, 'a', 'y', 'x'), '---')
      '---'

    '''
    return (source.pop(key) for key in keys if key in source)


def multi_get(source, *keys):
    '''Get values from `source` of all given `keys`.

    :param source: Any compatible mapping.

    :param keys: Keys to get values.

    All keys that are not found are ignored.

    Examples::

      >>> d = {'x': 1, 'y': 2, 'z': 3}
      >>> next(multi_get(d, 'a', 'y', 'x'), '---')
      2

      >>> next(multi_get(d, 'a', 'y', 'x'), '---')
      2

      >>> next(multi_get(d, 'a', 'b'), '---')
      '---'

    '''
    return (source.get(key) for key in keys if key in source)


def dict_update_new(target, source, fail=False):
    '''Update values in `source` that are new (not present) in `target`.

    If `fail` is True and a value is already set, an error is raised.

    '''
    for key in source:
        if key not in target:
            target[key] = source[key]
        elif fail:
            raise TypeError('key "{}" already in target'.format(key))


@deprecated('generator expression')
def fake_dict_iteritems(source):
    '''Iterate (key, value) in a source fake mapping.

    A fake mapping must define at least methods `keys` and
    `~object.__getitem__`:meth:.

    .. warning:: Deprecated since 1.7.0.  This was actually in risk since
                 1.4.0.

    '''
    import warnings
    warnings.warn('fake_dict_iteritems is in risk for deprecation')
    for key in source.keys():
        yield key, source[key]


def delete_duplicates(seq, key=lambda x: x):
    '''Remove all duplicate elements from `seq`.

    Two items ``x`` and ``y`` are considered equal (duplicates) if
    ``key(x) == key(y)``.  By default `key` is the identity function.

    Works with any sequence that supports `len`:func:,
    `~object.__getitem__`:meth:, and `addition <object.__add__>`:meth:.

    .. note:: ``seq.__getitem__`` should work properly with slices.

    The return type will be the same as that of the original sequence.

    .. versionadded:: 1.5.5

    .. versionchanged:: 1.7.4 Added the `key` argument. Clarified the
       documentation: `seq` should also implement the ``__add__`` method and
       that its ``__getitem__`` method should deal with slices.

    '''
    i, done = 0, set()
    while i < len(seq):
        k = key(seq[i])
        if k not in done:
            done.add(k)
            i += 1
        else:
            seq = seq[:i] + seq[i+1:]
    return seq


def iter_delete_duplicates(iter, key=lambda x: x):
    '''Yields non-repeating items from `iter`.

    `key` has the same meaning as in `delete_duplicates`:func:.

    Examples:

      >>> list(iter_delete_duplicates('AAAaBBBA'))
      ['A', 'a', 'B', 'A']

      >>> list(iter_delete_duplicates('AAAaBBBA', key=lambda x: x.lower()))
      ['A', 'B', 'A']

    .. versionadded:: 1.7.4

    '''
    last = object()  # a value we're sure `iter` won't produce
    for x in iter:
        k = key(x)
        if k != last:
            yield x
        last = k


def slides(iterable, width=2, fill=None):
    '''Creates a sliding window of a given `width` over an iterable::

        >>> list(slides(range(1, 11)))
        [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]

    If the iterator does not yield a width-aligned number of items, the last
    slice returned is filled with `fill` (by default None)::

        >>> list(slides(range(1, 11), width=3))   # doctest: +ELLIPSIS
        [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, None, None)]

    .. versionchanged:: 1.4.0 If the `fill` argument is a collection is cycled
                        over to get the filling, just like in `first_n`:func:.

    .. versionchanged:: 1.4.2 The `fill` argument now defaults to None,
                        instead of Unset.

    '''
    from itertools import cycle, repeat
    from collections import Iterable
    pos = 0
    res = []
    iterator = iter(iterable)
    current = next(iterator, Unset)
    while current is not Unset:
        if pos < width:
            res.append(current)
            current = next(iterator, Unset)
            pos = pos + 1
        else:
            yield tuple(res)
            res = []
            pos = 0
    if res:
        if isinstance(fill, Iterable):
            fill = cycle(fill)
        else:
            fill = repeat(fill)
        while pos < width:
            res.append(next(fill))
            pos += 1
        yield tuple(res)


def continuously_slides(iterable, width=2, fill=None):
    '''Similar to `slides`:func: but moves one item at the time (i.e
    continuously).

    `fill` is only used to fill the fist chunk if the `iterable` has less
    items than the `width` of the window.

    Example (generate a texts tri-grams)::

        >>> slider = continuously_slides(str('maupassant'), 3)
        >>> list(str('').join(chunk) for chunk in slider)
        ['mau', 'aup', 'upa', 'pas', 'ass', 'ssa', 'san', 'ant']

    '''
    i = iter(iterable)
    res = []
    while len(res) < width:
        current = next(i, fill)
        res.append(current)
    yield tuple(res)
    current = next(i, Unset)
    while current is not Unset:
        res.pop(0)
        res.append(current)
        yield tuple(res)
        current = next(i, Unset)


def first_n(iterable, n=1, fill=Unset):
    '''Takes the first `n` items from iterable.

    If there are less than `n` items in the iterable and `fill` is
    `~xoutil.Unset`:class:, a StopIteration exception is raised; otherwise
    it's used as a filling pattern as explained below.

    :param iterable: An iterable from which the first `n` items should be
                     collected.

    :param n: The number of items to collect
    :type n: int

    :param fill: The filling pattern to use. It may be:

                 - a collection, in which case `first_n` fills the last items
                   by cycling over `fill`.

                 - anything else is used as the filling pattern by repeating.

    :returns: The first `n` items from `iterable`, probably with a filling
              pattern at the end.
    :rtype: generator object

    .. versionadded:: 1.2.0

    .. versionchanged:: 1.4.0 The notion of collection for the `fill` argument
                        uses `xoutil.types.is_collection`:func: instead of
                        probing for the ``__iter__`` method.

    .. versionchanged:: 1.7.2 The notion of collection for the `fill` argument
                        uses ``isinstance(fill, Iterable)`` replacing
                        `xoutil.types.is_collection`:func:.  We must be
                        consistent with `iterable` argument that allow an
                        string as a valid iterable and `is_collection` not.

    '''
    if fill is not Unset:
        from collections import Iterable
        from itertools import cycle, repeat, chain
        if isinstance(fill, Iterable):
            fill = cycle(fill)
        else:
            fill = repeat(fill)
        seq = chain(iterable, fill)
    else:
        seq = iter(iterable)
    while n > 0:
        yield next(seq)
        n -= 1


def ungroup(iterator):
    '''Reverses the operation of `itertools.groupby`:func: (or similar).

    The `iterator` should produce pairs of ``(_, xs)``; where ``xs`` is
    another iterator (or iterable).

    It's guaranteed that the `iterator` will be consumed at the *boundaries*
    of each pair, i.e. before taking another pair ``(_, ys)`` from `iterator`
    the first ``xs`` will be fully yielded.

    Demonstration:

      >>> def groups():
      ...    def chunk(s):
      ...       for x in range(s, s+3):
      ...           print('Yielding x:', x)
      ...           yield x
      ...
      ...    for g in range(2):
      ...       print('Yielding group', g)
      ...       yield g, chunk(g)

      >>> list(ungroup(groups()))
      Yielding group 0
      Yielding x: 0
      Yielding x: 1
      Yielding x: 2
      Yielding group 1
      Yielding x: 1
      Yielding x: 2
      Yielding x: 3
      [0, 1, 2, 1, 2, 3]

    This is not the same as::

      >>> import itertools
      >>> xs = itertools.chain(*(xs for _, xs in groups()))
      Yielding group 0
      Yielding group 1

    Notice that the iterator was fully consumed just to create the arguments
    to ``chain()``.

    .. versionadded:: 1.7.3

    '''
    for _, xs in iterator:
        for x in xs:
            yield x


# Compatible zip and map
from xoutil.eight import python_version

if python_version == 3:
    map = map
    zip = zip
    from itertools import zip_longest     # noqa

else:
    from itertools import (imap as map, izip as zip,    # noqa
                           izip_longest as zip_longest)
