:mod:`xoutil.infinity` - An infinite value
==========================================

.. module:: xoutil.infinity

.. object:: xoutil.infinity.Infinity

   The positive infinite value.  The negative infinite value is ``-Infinity``.

   These values are only sensible for comparison.  Arithmetic is not
   supported.

   The type of values that is comparable with `Infinity`:obj: is controlled by
   the ABC `InfinityComparable`:class:.


.. autoclass:: xoutil.infinity.InfinityComparable
