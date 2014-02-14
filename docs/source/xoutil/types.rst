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

.. autoclass:: UnsetType

.. autoclass:: DictProxyType

.. autoclass:: SlotWrapperType

.. autoclass:: Required

.. autoclass:: mro_dict

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
