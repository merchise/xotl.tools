==============================================================
 `xotl.tools.fp.tools`:mod: -- High-level pure function tools
==============================================================

.. testsetup::

   from xotl.tools.fp.tools import *

.. automodule:: xotl.tools.fp.tools

.. class:: compose(*funcs)

   Composition of several functions.

   Functions are composed right to left.  A composition of zero functions
   gives back the `identity`:func: function.

   Rules must be fulfilled:

   .. doctest::

      >>> x = 15
      >>> f, g, h = x.__add__, x.__mul__, x.__xor__

      >>> compose() is identity
      True

      >>> compose(identity, f, identity) is f
      True

      >>> compose(f) is f
      True

      >>> compose(g, f)(x) == g(f(x))
      True

      >>> compose(h, g, f)(x) == h(g(f(x)))
      True

   If any "intermediate" function returns an instance of:

   - `pos_args`:class:\ : it's expanded as variable positional arguments to
     the next function.

   - `kw_args`:class:\ : it's expanded as variable keyword arguments to the
     next function.

   - `full_args`:class:\ : it's expanded as variable positional and keyword
     arguments to the next function.

   The expected usage of these is **not** to have function return those types
   directly, but to use them when composing functions that return tuples and
   expect tuples.


.. autofunction:: identity

.. autofunction:: fst

.. autofunction:: snd

.. autofunction:: constant

.. autoclass:: pos_args

.. autoclass:: kw_args

.. autoclass:: full_args
