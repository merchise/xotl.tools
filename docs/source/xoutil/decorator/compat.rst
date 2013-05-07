================================================================================
:mod:`xoutil.decorator.compat` -- Decorators for Python 2 and 3 interoperability
================================================================================

.. automodule:: xoutil.decorator.compat

.. autofunction:: metaclass(meta)

   .. warning::

      *Deprecated since 1.4.1, will be removed in 1.6.0*. You should use
      :func:`xoutil.objects.metaclass`.  This function is faster because it
      does not recreates the class like the decorator does.

      In a benchmark we have created with a dummy metaclass and fat class with
      102 attributes, we observe the following results for the new function::

	   >>> %timeit -n1000 inline_meta()
	   1000 loops, best of 3: 89.1 us per loop

      and for the decorator one::

	   >>> %timeit -n1000 deco_meta()
	   1000 loops, best of 3: 215 us per loop

      So the new function is about 2.4x faster than the deprecated decorator.
