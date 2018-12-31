`xotl.tools.future.threading`:mod: - Higher-level threading interface
=====================================================================

.. module:: xotl.tools.future.threading

This module extends the standard library's `threading`:mod:.  You may use it
as a drop-in replacement in many cases.

Avoid importing ``*`` from this module since could be different in Python 2.7
and Python 3.3.

We added the following features.

.. autofunction:: async_call

.. autofunction:: sync_call
