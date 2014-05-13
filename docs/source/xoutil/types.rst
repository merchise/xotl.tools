:mod:`xoutil.types` - Names for built-in types and extensions.
===============================================================

.. Unfortunately our customized modules is not compatible with sphinx
   automodule

.. module:: xoutil.types

.. autofunction:: is_iterable

.. autofunction:: is_collection

.. autofunction:: is_scalar

.. autofunction:: is_string_like

.. autofunction:: is_module

.. autofunction:: is_classmethod

.. autofunction:: is_staticmethod

.. autofunction:: is_instancemethod

.. autofunction:: is_slotwrapper

.. autofunction:: are_instances(*subjects, types)

.. autofunction:: no_instances(*subjects, types)

.. autofunction:: new_class

   .. versionadded:: 1.5.5

.. autofunction:: prepare_class

   .. versionadded:: 1.5.5

.. autoclass:: UnsetType

.. autoclass:: DictProxyType

.. autoclass:: SlotWrapperType

.. autoclass:: Required

.. autoclass:: mro_dict

.. class:: MappingProxyType

   .. versionadded:: 1.5.5

   Read-only proxy of a mapping. It provides a dynamic view on the mapping’s
   entries, which means that when the mapping changes, the view reflects these
   changes.

   .. note:: In Python 3.3+ this is an alias for
      :class:`types.MappingProxyType` in the standard library.


.. class:: SimpleNamespace

   .. versionadded:: 1.5.5

   A simple :class:`object` subclass that provides attribute access to its
   namespace, as well as a meaningful repr.

   Unlike :class:`object`, with ``SimpleNamespace`` you can add and remove
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
   However, for a structured record type use :func:`~collections.namedtuple`
   instead.

   .. note:: In Python 3.4+ this is an alias to
             :class:`types.SimpleNamespace`.

.. autoclass:: DynamicClassAttribute


.. _types-140-refactor:

Importing `Unset` and `ignored`
-------------------------------

.. warning:: Removed in 1.5.0

   .. deprecated:: 1.4.0 These imports are removed in version 1.5.0.

The values `Unset` and `ignored` are not types neither functions that test for
types.  They are values and are moved out of this module.  Nevertheless, they
will remain importable from this module up to version 1.5.0.

.. data:: Unset

   See :class:`UnsetType`.

.. data:: ignored

   To be used in arguments that are currently ignored cause they are being
   deprecated. The only valid reason to use `ignored` is to signal ignored
   arguments in method's/function's signature.
