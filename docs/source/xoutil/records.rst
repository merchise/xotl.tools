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

These functions have a `nullable` argument that indicates whether the value
must be present or not.  We won't document that argument in all the functions.

.. autofunction:: datetime_reader(format, nullable=False)

.. autofunction:: boolean_reader(true=('1', ), nullable=False)

.. autofunction:: integer_reader(nullable=False)

.. autofunction:: decimal_reader(nullable=False)

.. autofunction:: float_reader(nullable=False)
