`xoutil.future.inspect`:mod: - Inspect live objects
===================================================

.. module:: xoutil.future.inspect

This module extends the standard library's `functools`:mod:.  You may use it
as a drop-in replacement in many cases.

Avoid importing ``*`` from this module since could be different in Python 2.7
and Python 3.3.

We added the following features.

.. autofunction:: get_attr_value

.. autofunction:: type_name

We have backported several Python 3.3 features but maybe not all (some
protected structures are not presented in this documentation).

.. autofunction:: getfullargspec

.. autofunction:: getattr_static
