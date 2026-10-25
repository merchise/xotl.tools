====================================================================
 `xotl.tools.clipping`:mod: - Object string representation protocol
====================================================================

.. automodule:: xotl.tools.clipping
   :members: crop, crop_iterator

Migrating to reprlib
====================

Use `reprlib.repr`:func: for abbreviated representations with default limits, or configure a
`reprlib.Repr`:class: instance.  For compatibility with Python 3.10, set the instance attributes
rather than passing constructor keywords:

.. code-block:: python

   import reprlib

   formatter = reprlib.Repr()
   formatter.maxlevel = 3
   formatter.maxstring = 64
   formatter.maxother = 64
   text = formatter.repr(value)

These are limits on individual representations and nesting, not a strict total character budget.
``reprlib`` uses ``repr`` rather than the default ``str`` behavior of ``crop``, and does not honor
``__crop__``.  Review custom hooks, string quoting, function names, and ellipses when migrating;
the output is not guaranteed to match.

The ``fillvalue`` attribute was added in Python 3.11.  Constructor keyword configuration and
``indent`` were added in Python 3.12.  See the `reprlib documentation
<https://docs.python.org/3/library/reprlib.html>`_ for version-specific behavior.  This module
remains available until 4.0.0 so callers can migrate deliberately across supported Python versions.

The aliases ``small`` and ``short`` share ``crop``'s deprecation warning.  Constants and the
``__crop__`` protocol are also deprecated, but importing the module does not itself emit a warning.
