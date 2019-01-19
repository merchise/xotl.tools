`xotl.tools.future.textwrap`:mod: - Text wrapping and filling
=============================================================

.. module:: xotl.tools.future.textwrap

This module extends the standard library's `textwrap`:mod:.  You may use it as
a drop-in replacement in many cases.

Avoid importing ``*`` from this module since could be different in Python 2.7
and Python 3.3.

We added the following features.

.. autofunction:: dedent

We have backported several Python 3.3 features but maybe not all.

.. autofunction:: indent
