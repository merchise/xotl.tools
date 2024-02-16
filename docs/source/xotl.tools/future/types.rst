`xotl.tools.future.types`:mod: - Names for built-in types and extensions
========================================================================

.. module:: xotl.tools.future.types

This module extends the standard library's `functools`:mod:.  You may use it
as a drop-in replacement in many cases.

Avoid importing ``*`` from this module since could be different in Python 2.7
and Python 3.3.

We added mainly compatibility type definitions, those that each one could be in one
version and not in other.

.. autofunction:: new_class

   .. versionadded:: 1.5.5

.. autofunction:: prepare_class

   .. versionadded:: 1.5.5

.. class:: MappingProxyType

   .. versionadded:: 1.5.5

   Read-only proxy of a mapping. It provides a dynamic view on the mapping’s
   entries, which means that when the mapping changes, the view reflects these
   changes.

   .. note:: In Python 3.3+ this is an alias for
      `types.MappingProxyType`:class: in the standard library.
