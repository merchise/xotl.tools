:mod:`xoutil.iterators` -   Functions creating iterators for efficient looping
==============================================================================

.. automodule:: xoutil.iterators
   :members: dict_update_new, first_n, first_non_null,
	     slides, continuously_slides, delete_duplicates

.. autofunction:: fake_dict_iteritems(source)

.. autofunction:: flatten(sequence, is_scalar=xoutil.types.is_scalar, depth=None)

.. function:: xoutil.iterators.zip([iter1[, iter2[, ...]]])

   Return a zip-like object whose `next()` method returns a tuple where the
   i-th element comes from the i-th iterable argument. The `next()` method
   continues until the shortest iterable in the argument sequence is exhausted
   and then it raises StopIteration.

   This method is actually the standard ``itertools.izip()`` when in Python
   2.7, and the builtin ``zip`` when in Python 3.

.. function:: xoutil.iterators.map(func, *iterables)

   Make an iterator that computes the function using arguments from each of the
   iterables. It stops when the shortest iterable is exhausted instead of
   filling in None for shorter iterables.

   This method is actually the stardard ``itertools.imap`` when in Python 2.7,
   and the builtin ``map`` when in Python 3.

.. function:: xoutil.iterators.zip_longest(*iterables, fillvalue=None)

   Make an iterator that aggregates elements from each of the iterables. If the
   iterables are of uneven length, missing values are filled-in with
   fillvalue. Iteration continues until the longest iterable is
   exhausted.

   If one of the iterables is potentially infinite, then the
   :func:`zip_longest` function should be wrapped with something that limits
   the number of calls (for example :func:`islice` or :func:`takewhile`). If
   not specified, `fillvalue` defaults to None.

   This function is actually an alias to :func:`itertools.izip_longest` in
   Python 2.7, and an alias to :func:`itertools.zip_longest` in Python
   3.3.
