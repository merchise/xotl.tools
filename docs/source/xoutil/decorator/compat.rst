================================================================================
:mod:`xoutil.decorator.compat` -- Decorators for Python 2 and 3 interoperability
================================================================================

.. automodule:: xoutil.decorator.compat

.. autofunction:: metaclass(meta)

   .. warning::

      *Deprecated since 1.4.1*. Use :func:`xoutil.objects.metaclass`.  That
      function is deemed more optimal since it does not copies the class.

      As benchmark we have created two functions with a class with 102
      attributes. Each with a dumb metaclass::

        class Meta(type):
            pass

      and a fat class of 102 attributes::

        class Foobar(object):
            def __init__(self, name):
                self.name = name

            a0 = 0
            a1 = 1
            a2 = 2
            a3 = 3
            # ... more ...
            a100 = 100

      In the function `inline_meta` we declare the metaclass using the brand
      new (and as you'll faster) :func:`xoutil.objects.metaclass`; and in the
      `deco_meta` we use the decorator alternative.

      The results are::


	   >>> %timeit -n1000 inline_meta()
	   1000 loops, best of 3: 89.1 us per loop

	   >>> %timeit -n1000 deco_meta()
	   1000 loops, best of 3: 215 us per loop
