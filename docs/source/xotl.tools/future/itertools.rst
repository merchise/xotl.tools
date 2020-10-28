`xotl.tools.future.itertools`:mod: - Functions creating iterators for efficient looping
=======================================================================================

.. automodule:: xotl.tools.future.itertools
   :members: dict_update_new, first_n, first_non_null,
	         slides, continuously_slides, ungroup

.. function:: merge(*iterables, key=None)

   Merge the iterables in order.

   Return an iterator that yields all items from `iterables` following the
   order given by `key`.  If `key` is not given we compare the items.

   If the `iterables` yield their items in increasing order (w.r.t `key`), the
   result is also ordered (like a merge sort).

   ``merge()`` returns the *empty* iterator.

   .. versionadded:: 1.8.4

   .. versionchanged:: 2.1.0 Based on `heapq.merge`:func:.  In Python
      3.5+, this is just an alias of it.

   .. deprecated:: 2.1.0 Use `heapq.merge`:func: directly.  This function will
                   be removed when we support for Python 3.4.

.. autofunction:: delete_duplicates(seq[, key=lambda x: x])

.. autofunction:: iter_delete_duplicates(iter[, key=lambda x: x])

.. autofunction:: iter_without_duplicates(iter[, key=lambda x: x])

.. autofunction:: flatten(sequence, is_scalar=xotl.tools.types.is_scalar, depth=None)

.. function:: xotl.tools.iterators.zip([iter1[, iter2[, ...]]])

   Return a zip-like object whose `next()` method returns a tuple where the
   i-th element comes from the i-th iterable argument. The `next()` method
   continues until the shortest iterable in the argument sequence is exhausted
   and then it raises StopIteration.

   .. deprecated:: 2.1.0 Use the builtin `zip`:func:.  This function will be
                   removed in xotl.tools 3.


.. function:: xotl.tools.iterators.map(func, *iterables)

   Make an iterator that computes the function using arguments from each of the
   iterables. It stops when the shortest iterable is exhausted instead of
   filling in None for shorter iterables.

   .. deprecated:: 2.1.0 Use the builtin `map`:func:.  This function will be
                   removed in xotl.tools 3.

.. function:: xotl.tools.iterators.zip_longest(*iterables, fillvalue=None)

   Make an iterator that aggregates elements from each of the iterables. If the
   iterables are of uneven length, missing values are filled-in with
   fillvalue. Iteration continues until the longest iterable is
   exhausted.

   If one of the iterables is potentially infinite, then the
   `zip_longest`:func: function should be wrapped with something that limits
   the number of calls (for example `islice`:func: or `takewhile`:func:).  If
   not specified, `fillvalue` defaults to None.

   This function is actually an alias to `itertools.izip_longest`:func: in
   Python 2.7, and an alias to `itertools.zip_longest`:func: in Python
   3.3.


.. autofunction:: zip_map(funcs: Iterable[Callable[[A], B]], args: Iterable[A]) -> Iterable[B]
