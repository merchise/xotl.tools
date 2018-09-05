#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Several util functions for iterators.

.. versionchanged:: 1.8.4 Renamed to `xoutil.future.iterator`:mod:.  The
   ``xoutil.iterators`` is now a deprecated alias.

'''
from itertools import *  # noqa

map = map
zip = zip

from xoutil.symbols import Unset


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
    iterables -but strings- will be considered as scalars.

    For example::

        >>> from xoutil.eight import range
        >>> range_ = lambda *a: list(range(*a))
        >>> tuple(flatten((1, range_(2, 5), range(5, 10))))
        (1, 2, 3, 4, 5, 6, 7, 8, 9)

    If `depth` is None the collection is flattened recursively until the
    "bottom" is reached.  If `depth` is an integer then the collection is
    flattened up to that level.  `depth=0` means not to flatten.  Nested
    iterators are not "exploded" if under the stated `depth`::

        # In the following doctest we use ``...range(...X)`` because the
        # string repr of range differs in Py2 and Py3k.

        >>> tuple(flatten((range_(2), range(2, 4)), depth=0))  # doctest: +ELLIPSIS  # noqa
        ([0, 1], ...range(2, 4))

        >>> tuple(flatten((range(2), range_(2, 4)), depth=0))  # doctest: +ELLIPSIS  # noqa
        (...range(...2), [2, 3])

    .. note:: Compatibility issue

       In Python 2 ``bytes`` is the standard string but in Python 3 is a
       binary buffer, so ``flatten([b'abc', [1, 2, 3]])`` will deliver
       different results.

    '''
    if is_scalar is None:
        def is_scalar(maybe):
            '''Returns if `maybe` is not not an iterable or a string.'''
            from collections import Iterable
            from xoutil.eight import string_types as strs
            return isinstance(maybe, strs) or not isinstance(maybe, Iterable)
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
            seq = seq[:i] + seq[i + 1:]
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
    `~xoutil.symbols.Unset`:class:, a StopIteration exception is raised;
    otherwise it's used as a filling pattern as explained below.

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
                        uses ``xoutil.types.is_collection`` instead of probing
                        for the ``__iter__`` method.

    .. versionchanged:: 1.7.2 The notion of collection for the `fill` argument
                        uses ``isinstance(fill, Iterable)`` replacing
                        ``xoutil.types.is_collection``.  We must be consistent
                        with `iterable` argument that allow an string as a
                        valid iterable and `is_collection` not.

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
    try:
        while n > 0:
            yield next(seq)
            n -= 1
    except StopIteration:
        # Python 3.7+ (PEP 479) does not bubbles the StopIteration, but
        # converts it to RuntimeError.  Using `return` restores the <3.7
        # behavior.
        return


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


def merge(*iterables, key=None):
    '''Merge the iterables in order.

    Return an iterator that yields all items from `iterables` following the
    order given by `key`.  If `key` is not given we compare the items.

    If the `iterables` yield their items in order (w.r.t `key`), the result is
    also ordered (like a merge sort).

    ``merge()`` returns the *empty* iterator.

    .. versionadded:: 1.8.4

    '''
    from xoutil.symbols import Undefined
    from xoutil.future.collections import Iterable, Iterator

    if key is None:
        key = lambda x: x

    def _merge(iter1, iter2):
        iter1 = iter(iter1)
        iter2 = iter(iter2)
        item1 = next(iter1, Undefined)
        item2 = next(iter2, Undefined)
        while item1 is not Undefined and item2 is not Undefined:
            if key(item1) <= key(item2):
                yield item1
                item1 = next(iter1, Undefined)
            else:
                yield item2
                item2 = next(iter2, Undefined)
        # One of the iterators (or both) has been exhausted, consume the
        # other.
        while item1 is not Undefined:
            yield item1
            item1 = next(iter1, Undefined)
        while item2 is not Undefined:
            yield item2
            item2 = next(iter2, Undefined)

    def _empty():
        return
        yield

    if not all(isinstance(iter_, (Iterable, Iterator)) for iter_ in iterables):
        raise TypeError('Positional argument must be iterables or iterators')
    if iterables:
        res = iterables[0]
        for iter_ in iterables[1:]:
            res = _merge(res, iter_)
    else:
        res = _empty()
    return res
