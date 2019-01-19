=================================================
 `xotl.tools.records`:mod: - Records definitions
=================================================

.. automodule:: xotl.tools.records

.. autoclass:: record

.. _included-readers:

Included reader builders
========================

The following functions *build* readers for standards types.

.. note:: You cannot use these functions themselves as readers, but you must
	  call them to obtain the desired reader.

All these functions have a pair of keywords arguments `nullable` and
`default`.  The argument `nullable` indicates whether the value must be
present or not.  The function `check_nullable`:func: implements this check and
allows other to create their own builders with the same semantic.

.. autofunction:: datetime_reader(format, nullable=False, default=None, strict=True)

.. autofunction:: boolean_reader(true=('1', ), nullable=False, default=None)

.. autofunction:: integer_reader(nullable=False, default=None)

.. autofunction:: decimal_reader(nullable=False, default=None)

.. autofunction:: float_reader(nullable=False, default=None)

.. autofunction:: date_reader(format, nullable=False, default=None, strict=True)

Checking for null values
------------------------

.. autofunction:: isnull
.. autofunction:: check_nullable(val, nullable)


These couple of functions allows you to define new builders that use the same
null concept.  For instance, if you need readers that parse dates in diferent
locales you may do::

    def date_reader(nullable=False, default=None, locale=None):
	from xotl.tools.records import check_nullable
	from babel.dates import parse_date, LC_TIME
	from datetime import datetime
	if not locale:
	    locale = LC_TIME

	def reader(value):
	    if check_nullable(value, nullable):
	        return parse_date(value, locale=locale)
	    else:
		return default
	return reader
