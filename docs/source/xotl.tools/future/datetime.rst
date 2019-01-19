`xotl.tools.future.datetime`:mod: - Basic date and time types
=============================================================

.. module:: xotl.tools.future.datetime

This module extends the standard library's `datetime`:mod:.  You may use it
as a drop-in replacement in many cases.

Avoid importing ``*`` from this module since could be different in Python 2.7
and Python 3.3.

In Pytnon versions <= 3 date format fails for several dates, for example
``date(1800, 1, 1).strftime("%Y")``.  So, classes `~datetime.date`:class: and
`~datetime.datetime`:class: are redefined if that case.

This problem could be solved by redefining the `strftime` function in the
`time` module, because it is used for all `strftime` methods; but (WTF),
Python double checks the year (in each method and then again in
`time.strftime` function).

.. autofunction:: assure

We added the following features.

.. autofunction:: strfdelta
.. autofunction:: strftime
.. autofunction:: get_month_first
.. autofunction:: get_month_last
.. autofunction:: get_next_month
.. autofunction:: is_full_month

.. autoclass:: flextime

.. autofunction:: daterange([start,] stop[, step])

.. autoclass:: DateField

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

   .. automethod:: __contains__

   .. automethod:: __and__
   .. method:: __mul__

      An alias for `__and__`:meth:.

   .. automethod:: intersection

   .. automethod:: __lshift__

   .. automethod:: __rshift__

   .. automethod:: __len__

   .. automethod:: diff


.. autoclass:: DateTimeSpan

   .. automethod:: from_datetime
   .. automethod:: from_timespan

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

   .. automethod:: __contains__

   .. automethod:: __and__
   .. method:: __mul__

      An alias for `__and__`:meth:.

   .. automethod:: intersection

   .. automethod:: __lshift__

   .. automethod:: __rshift__

   .. automethod:: __len__

   .. automethod:: diff


.. data:: EmptyTimeSpan

   The empty time span.  It's not an instance of `TimeSpan`:class: but engage
   set-like operations: union, intersection, etc.

   No date is a member of the empty time span.  The empty time span is a
   proper subset of any time span.  It's only a superset of itself.  It's not
   a proper superset of any other time span nor itself.

   This instance is a singleton.
