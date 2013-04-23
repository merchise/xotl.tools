:mod:`xoutil.types` - Names for built-in types and extensions.
===============================================================

.. automodule:: xoutil.types
   :members: is_iterable, is_collection, is_scalar, is_string_like, is_module,
	     is_classmethod, is_staticmethod, is_instancemethod,
	     is_slotwrapper, UnsetType, DictProxyType, SlotWrapperType,
	     Required, mro_dict



.. _types-140-refactor:

Importing `Unset` and `ignored`
-------------------------------

The values `Unset` and `ignored` are not types neither functions that test for
types. They are values and are moved out of this module. Nevertheless, they
will remain importable from this module up to version 1.5.0.

.. data:: Unset

   See :class:`UnsetType`.

   .. warning:: Import directly from `xoutil`, importing Unset from
		`xoutil.types` is deprecated since 1.4.0


.. data:: ignored

   To be used in arguments that are currently ignored cause they are being
   deprecated. The only valid reason to use `ignored` is to signal ignored
   arguments in method's/function's signature.

   .. warning:: Importing `ignored` from `xoutil.types` is deprecated since
		1.4.0. You must import `Ignored` from `xoutil` directly::

		    from xoutil import Ignored
