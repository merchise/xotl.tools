:mod:`xoutil.iterators` -   Functions creating iterators for efficient looping
==============================================================================

.. automodule:: xoutil.iterators
   :members: dict_update_new, fake_dict_iteritems, first_n, first_non_null,
	     slides

.. autofunction:: smart_dict(defaults, *sources)

.. autofunction:: obtain(predicate, default=None)

.. autofunction:: flatten(sequence, is_scalar=xoutil.types.is_scalar, depth=None)

.. autofunction:: get_flat_list(iterable)

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

.. function:: xoutil.iterators.izip

   An alias to :func:`zip`.

.. function:: xoutil.iterators.imap

   An alias to :func:`map`.
