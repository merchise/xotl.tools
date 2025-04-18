#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""Several util functions for iterators.

.. versionchanged:: 1.8.4 Renamed to `xotl.tools.future.iterator`:mod:.  The
   ``xotl.tools.iterators`` is now a deprecated alias.

"""

from typing import Any, Callable, Iterable, Iterator, List, Optional, Tuple, TypeVar, Union, cast

from xotl.tools.symbols import Unset

T = TypeVar("T")
X = TypeVar("X")
V = TypeVar("V")


def first_non_null(
    iterable: Iterable[X],
    default: Optional[V] = None,
    *,
    key: Optional[Callable[[X], Any]] = None,
    getvalue: Optional[Callable[[X], Optional[V]]] = None,
) -> Optional[V]:
    """Returns the first value from iterable which is non-null w.r.t to the key.

    This is roughly the same as::

         next((getvalue(x) for x in iterable if key(x)), default)

    Use the identity (``lambda x: x``) for `key` and/or `getvalue` if None.

    .. versionadded:: 1.4.0

    .. versionchanged:: 3.4.0 Added arguments `key` and `getvalue`.

    """
    if key is None:
        key = cast(Callable[[X], X], lambda x: x)
    if getvalue is None:
        get = cast(Callable[[X], Optional[V]], lambda x: x)
    else:
        get = getvalue
    return next((get(x) for x in iterable if key(x)), default)


def flatten(sequence, is_scalar=None, depth=None):
    """Flatten-out a sequence.

    It takes care of everything deemed a collection (i.e, not a scalar
    according to the callable passed in `is_scalar` argument; if ``None``,
    iterables -but strings- will be considered as scalars.

    For example::

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

    """
    if is_scalar is None:

        def is_scalar(maybe):
            """Returns if `maybe` is not not an iterable or a string."""
            from collections.abc import Iterable

            return isinstance(maybe, str) or not isinstance(maybe, Iterable)

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
    """Pop first value from `source` from given `keys`.

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

    """
    return next((source.pop(key) for key in keys if key in source), default)


def multi_pop(source, *keys):
    """Pop values from `source` of all given `keys`.

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

    """
    return (source.pop(key) for key in keys if key in source)


def multi_get(source, *keys):
    """Get values from `source` of all given `keys`.

    :param source: Any compatible mapping.

    :param keys: Keys to get values.

    All keys that are not found are ignored.

    Examples::

      >>> d = {'x': 1, 'y': 2, 'z': 3}
      >>> next(multi_get(d, 'a', 'y', 'x'), '---')
      2

      >>> next(multi_get(d, 'a', 'b'), '---')
      '---'

    """
    return (source.get(key) for key in keys if key in source)


def dict_update_new(target, source, fail=False):
    """Update values in `source` that are new (not present) in `target`.

    If `fail` is True and a value is already set, an error is raised.

    """
    for key in source:
        if key not in target:
            target[key] = source[key]
        elif fail:
            raise TypeError('key "{}" already in target'.format(key))


def delete_duplicates(seq, key=lambda x: x):
    """Remove all duplicate elements from `seq`.

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

    """
    i, done = 0, set()
    while i < len(seq):
        k = key(seq[i])
        if k not in done:
            done.add(k)
            i += 1
        else:
            seq = seq[:i] + seq[i + 1 :]
    return seq


def iter_delete_duplicates(
    iter: Iterable[T],
    key: Callable[[T], Any] = lambda x: x,
) -> Iterator[T]:
    """Yields non-repeating (and consecutive) items from `iter`.

    `key` has the same meaning as in `delete_duplicates`:func:.

    Examples:

      >>> list(iter_delete_duplicates('AAAaBBBA'))
      ['A', 'a', 'B', 'A']

      >>> list(iter_delete_duplicates('AAAaBBBA', key=lambda x: x.lower()))
      ['A', 'B', 'A']

    .. versionadded:: 1.7.4

    """
    last = object()  # a value we're sure `iter` won't produce
    for x in iter:
        k = key(x)
        if k != last:
            yield x
        last = k


def iter_without_duplicates(
    it: Iterable[T],
    key: Callable[[T], Any] = lambda x: x,
) -> Iterator[T]:
    """Yields non-repeating items from `iter`.

    `key` has the same meaning as in `delete_duplicates`:func:.

    The difference between this function and `iter_delete_duplicates`:func: is
    that we ensure the same item (as per `key`) is produced only once; while
    `iter_delete_duplicates`:func: only remove consecutive repeating items.

    Example:

      >>> list(iter_without_duplicates('AAAaBBBA', key=lambda x: x.lower()))
      ['A', 'B']


    """
    done = set()
    for what in it:
        k = key(what)
        if k not in done:
            yield what
            done.add(k)


#: A sentinel value to make `slides`:func: not to fill the last chunk.
NO_FILL = object()


def slides(
    iterable: Iterable[T],
    width: int = 2,
    fill: Optional[X] = None,
) -> Iterator[Tuple[Union[T, X, None], ...]]:
    """Creates a sliding window of a given `width` over an iterable::

        >>> list(slides(range(1, 11)))
        [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]

    If the iterator does not yield a width-aligned number of items, the last
    slice returned is filled with `fill` (by default None) unless `fill` is
    :any:`NO_FILL`::

        >>> list(slides(range(1, 11), width=3))
        [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, None, None)]

        >>> list(slides(range(1, 11), width=3, fill=NO_FILL))
        [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10,)]

    .. versionchanged:: 1.4.0 If the `fill` argument is a collection is cycled
                        over to get the filling, just like in `first_n`:func:.

    .. versionchanged:: 1.4.2 The `fill` argument now defaults to None,
                        instead of Unset.

    .. versionchanged:: 2.2.2 The `fill` argument can now take the contant `NO_FILL`:any:

    """
    from collections.abc import Iterable
    from itertools import cycle, repeat

    pos = 0
    res: List[Union[T, X, None]] = []
    iterator = iter(iterable)
    unset = cast(T, Unset)
    current = next(iterator, unset)
    while current is not unset:
        if pos < width:
            res.append(current)
            current = next(iterator, unset)
            pos = pos + 1
        else:
            yield tuple(res)
            res = []
            pos = 0
    if res:
        if isinstance(fill, Iterable):
            filler: Iterator[Optional[X]] = cycle(fill)
        else:
            filler = repeat(fill)
        while pos < width:
            res.append(next(filler))
            pos += 1
        yield tuple(item for item in res if item is not NO_FILL)


def continuously_slides(
    iterable: Iterable[T],
    width: int = 2,
    fill: Optional[X] = None,
) -> Iterator[Tuple[Optional[Union[T, X]], ...]]:
    """Similar to `slides`:func: but moves one item at the time (i.e
    continuously).

    `fill` is only used to fill the fist chunk if the `iterable` has less
    items than the `width` of the window.

    Example (generate a texts tri-grams)::

        >>> slider = continuously_slides(str('maupassant'), 3)
        >>> list(str('').join(chunk) for chunk in slider)
        ['mau', 'aup', 'upa', 'pas', 'ass', 'ssa', 'san', 'ant']

    """
    i = iter(iterable)
    res: List[Union[T, X, None]] = []
    while len(res) < width:
        current = next(i, fill)
        res.append(current)
    yield tuple(res)
    unset = cast(T, Unset)
    current = next(i, unset)
    while current is not unset:
        res.pop(0)
        res.append(current)
        yield tuple(res)
        current = next(i, unset)


def ungroup(iterator: Iterable[Tuple[X, Iterable[T]]]) -> Iterator[T]:
    """Reverses the operation of `itertools.groupby`:func: (or similar).

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

    """
    for _, xs in iterator:
        for x in xs:
            yield x


A = TypeVar("A")
B = TypeVar("B")


def zip_map(funcs: Iterable[Callable[[A], B]], args: Iterable[A]) -> Iterator[B]:
    """Apply each function in `funcs` to its corresponding arguments.

    If the iterables are not of the same length, stop as soon as the shortest
    is exhausted.

    .. versionadded:: 2.1.9

    """
    for fn, arg in zip(funcs, args):
        yield fn(arg)
