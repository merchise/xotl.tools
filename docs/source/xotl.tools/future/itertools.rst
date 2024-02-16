`xotl.tools.future.itertools`:mod: - Functions creating iterators for efficient looping
=======================================================================================

.. testsetup::

   from xotl.tools.future.itertools import *

.. automodule:: xotl.tools.future.itertools
   :members: dict_update_new, first_non_null,
	         slides, continuously_slides, ungroup

.. autofunction:: delete_duplicates(seq[, key=lambda x: x])

.. autofunction:: iter_delete_duplicates(iter[, key=lambda x: x])

.. autofunction:: iter_without_duplicates(iter[, key=lambda x: x])

.. autofunction:: flatten(sequence, is_scalar=xotl.tools.types.is_scalar, depth=None)

.. autofunction:: zip_map(funcs: Iterable[Callable[[A], B]], args: Iterable[A]) -> Iterable[B]

.. data:: NO_FILL

   A sentinel value to make `slides`:func: not to fill the last chunk.
