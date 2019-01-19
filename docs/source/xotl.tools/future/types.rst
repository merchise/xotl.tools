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

.. class:: SimpleNamespace

   .. versionadded:: 1.5.5

   A simple `object`:class: subclass that provides attribute access to its
   namespace, as well as a meaningful repr.

   Unlike `object`:class:, with ``SimpleNamespace`` you can add and remove
   attributes.  If a ``SimpleNamespace`` object is initialized with keyword
   arguments, those are directly added to the underlying namespace.

   The type is roughly equivalent to the following code::

       class SimpleNamespace(object):
           def __init__(self, **kwargs):
               self.__dict__.update(kwargs)
           def __repr__(self):
               keys = sorted(self.__dict__)
               items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
               return "{}({})".format(type(self).__name__, ", ".join(items))
           def __eq__(self, other):
               return self.__dict__ == other.__dict__

   ``SimpleNamespace`` may be useful as a replacement for ``class NS: pass``.
   However, for a structured record type use `~collections.namedtuple`:func:
   instead.

   .. note:: In Python 3.4+ this is an alias to
             `types.SimpleNamespace`:class:.

.. autoclass:: DynamicClassAttribute
