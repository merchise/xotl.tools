============================================
:mod:`xoutil.records` - Records definitions.
============================================

.. automodule:: xoutil.records

.. autoclass:: record

.. _included-readers:

Included reader builders
========================

The following functions *build* readers for standards types.

.. note:: You cannot use these functions themselves as readers, but you must
	  call them to obtain the desired reader.

All these functions have a pair of keywords arguments `nullable` and
`default`.  The argument `nullable` indicates whether the value must be
present or not.  If `nullable` is True and the value is null-like, then the
default is returned by the readers.

.. note:: Null values are the empty string, None and any instance of
   `xoutil.types.UnsetType`:class:.  Notice that 0, the empty list and tuple
   are not considered null in this regards.  This allows that CSV nulls (the
   empty string) are correctly treated while other sources that provide
   numbers are not miss-interpreted.

.. autofunction:: datetime_reader(format, nullable=False, default=None)

.. autofunction:: boolean_reader(true=('1', ), nullable=False, default=None)

.. autofunction:: integer_reader(nullable=False, default=None)

.. autofunction:: decimal_reader(nullable=False, default=None)

.. autofunction:: float_reader(nullable=False, default=None)
