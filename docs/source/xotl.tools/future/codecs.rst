`xotl.tools.future.codecs`:mod: - Codec registry, base classes and tools
========================================================================

.. module:: xotl.tools.future.codecs

This module extends the standard library's `functools`:mod:.  You may use it
as a drop-in replacement in many cases.

Avoid importing ``*`` from this module since could be different in Python 2.7
and Python 3.3.

We added the following features.

.. autofunction:: force_encoding

.. autofunction:: safe_decode

.. autofunction:: safe_encode
