:mod:`xoutil.annotate` - Py3k compatible annotations for Python 2
=================================================================

.. automodule:: xoutil.annotate

.. note:: The `signature` argument for the :func:`annotate` in this module may
	  not work on other python implementations than CPython. Currently,
	  Pypy passes all but local variable tests.

.. autofunction:: xoutil.annotate.annotate(signature=None, **annotations)
