`xotl.tools.future.json`:mod: - Encode and decode the JSON format
=================================================================

.. module:: xotl.tools.future.json

This module extends the standard library's `json`:mod:.  You may use it
as a drop-in replacement in many cases.

Avoid importing ``*`` from this module since could be different in Python 2.7
and Python 3.3.

We added the following features.

.. autoclass:: JSONEncoder

.. autofunction:: encode_string
