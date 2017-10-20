`xoutil.future.string`:mod: - Common string operations
======================================================

.. module:: xoutil.future.string

This module extends the standard library's `string`:mod:.  You may use it
as a drop-in replacement in many cases.

Avoid importing ``*`` from this module since could be different in Python 2.7
and Python 3.3.

We added the following features.

.. autofunction:: cut_prefix

.. autofunction:: cut_any_prefix

.. autofunction:: cut_prefixes

.. autofunction:: cut_suffix

.. autofunction:: cut_any_suffix

.. autofunction:: cut_suffixes

.. autofunction:: normalize_str

.. autofunction:: normalize_slug

.. autofunction:: strfnumber

.. autofunction:: parse_boolean

.. autofunction:: parse_url_int

.. autofunction:: error2str

.. autofunction:: make_a10z

.. autofunction:: crop

.. autofunction:: crop_iterator

.. autofunction:: small
