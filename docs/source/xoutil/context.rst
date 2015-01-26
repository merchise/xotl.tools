:mod:`xoutil.context` - Simple execution contexts
=================================================

.. automodule:: xoutil.context
   :members: context, Context


.. _context-greenlets:

.. note:: About thread-locals and contexts.

   The `context`:class: uses internally a "thread-local" variable to keep
   context stacks in different threads from seeing each other.  If `gevent` is
   installed the `gevent.local` module is used instead of the standard
   library.

   If you uses collaborative multi-tasking based in other framework other than
   `gevent`, you must ensure to monkey patch the `threading.local` class so
   that isolation is kept.
