`xotl.tools.future.csv`:mod: - CSV parsing and writing extensions
=================================================================

.. module:: xotl.tools.future.csv

.. versionadded:: 1.8.4

This module extends the standard library's `csv`:mod:.  You may use it
as a drop-in replacement in many cases.

Avoid importing ``*`` from this module since could be different in Python 2.7
and Python 3.3.

We added the following features.

.. autoclass:: unix_dialect

   Added only in Python 2 for compatibility purposes.

.. autofunction:: parse
