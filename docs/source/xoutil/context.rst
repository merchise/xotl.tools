:mod:`xoutil.context` - Simple execution contexts
=================================================

.. automodule:: xoutil.context
   :members: context, Context


.. _context-greenlets:

.. note:: About thread-locals and contexts.

   This version (``xoutil-1.6.10+threaded``) does not use the greenlet
   isolation provided by the standard ``1.6.10``.

   In some environments we have found the greenlet module installed (even
   required by some packages) but unused (no loop that holds a reference to
   all greenlets).  In this cases our current implementation fails when the
   greenlets are garbage-collected.

   This release will always use the ``thread.local``.
