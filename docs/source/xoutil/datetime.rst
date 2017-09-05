:mod:`xoutil.datetime` - Basic date and time types
===================================================

.. automodule:: xoutil.datetime

.. autofunction:: new_date
.. autofunction:: new_datetime
.. autofunction:: strfdelta
.. autofunction:: strftime
.. autofunction:: get_month_first
.. autofunction:: get_month_last
.. autofunction:: get_next_month
.. autofunction:: is_full_month
.. autofunction:: daterange([start,] stop[, step])

.. autoclass:: TimeSpan

   .. automethod:: from_date

   .. autoattribute:: past_unbound
   .. autoattribute:: future_unbound
   .. autoattribute:: unbound
   .. autoattribute:: bound
   .. autoattribute:: valid

   .. automethod:: __le__
   .. method:: issubset

      An alias for `__le__`:meth:.

   .. automethod:: __ge__
   .. method:: issuperset

      An alias for `__ge__`:meth:.

   .. method:: covers

      An alias for `__ge__`:meth:.

   .. automethod:: isdisjoint
   .. automethod:: overlaps

   .. automethod:: __and__
   .. method:: __mul__

      An alias for `__and__`:meth:.

   .. automethod:: intersection

   .. automethod:: __or__
   .. method:: __add__

      An alias for `__or__`:meth:.

   .. automethod:: union


.. object:: EmptyTimeSpan

   The empty time span.  It's not an instance of `TimeSpan`:class: but engage
   set-like operations: union, intersection, etc.

   No date is a member of the empty time span.  The empty time span is a
   proper subset of any time span.  It's only a superset of itself.  It's not
   a proper superset of any other time span nor itself.
