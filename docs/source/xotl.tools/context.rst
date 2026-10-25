`xotl.tools.context`:mod: - Simple execution contexts
=====================================================

.. testsetup::

   from xotl.tools.context import *

.. automodule:: xotl.tools.context
   :members: context, Context

.. _context-greenlets:

.. note:: About isolation of contexts.

   The `context`:class: is implemented over `contextvars`:mod:.  Context stacks
   are isolated between threads, ``asyncio`` tasks and ``greenlets``.  Tasks
   created inside a context inherit a copy of the active contexts, and nested
   entries never leak back to the parent.

   .. versionchanged:: 3.4.0 Reimplemented over `contextvars`:mod:, replacing the
      ``threading.local`` and greenlet-local shims.  Import order with ``greenlet`` no longer
      matters.

   .. versionchanged:: 1.7.1 Changed the test about ``greenlet``.  Instead of testing for `greenlet`
      to be importable, test it is imported already.

   .. versionchanged:: 1.6.9 Added direct greenlet isolation and removed the need for
      `gevent.local`:mod:.

   .. versionadded:: 1.6.8 Uses `gevent.local`:mod: if available to isolate greenlets.
