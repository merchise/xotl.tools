`xotl.tools.future.datetime`:mod: - Basic date and time types
=============================================================

.. testsetup::

   from xotl.tools.future.datetime import *


.. module:: xotl.tools.future.datetime

This module complements the standard library's `datetime`:mod:.

We added the following features.

.. autofunction:: strfdelta
.. autofunction:: strftime
.. autofunction:: get_month_first
.. autofunction:: get_month_last
.. autofunction:: get_next_month
.. autofunction:: is_full_month

.. function:: get_next_monday(ref)
.. function:: get_next_tuesday(ref)
.. function:: get_next_wednesday(ref)
.. function:: get_next_thursday(ref)
.. function:: get_next_friday(ref)
.. function:: get_next_saturday(ref)
.. function:: get_next_sunday(ref)
.. function:: get_previous_monday(ref)
.. function:: get_previous_tuesday(ref)
.. function:: get_previous_wednesday(ref)
.. function:: get_previous_thursday(ref)
.. function:: get_previous_friday(ref)
.. function:: get_previous_saturday(ref)
.. function:: get_previous_sunday(ref)

   These family of functions compute the next/previous date per calendar
   weekday.

   The argument to `ref` could be either a `datetime.datetime`:class: or
   `datetime.date`:class: and the result will match the input.

   If `ref` is a datetime the time-related components are kept the same.

   Examples:

   .. doctest::

      >>> d = datetime(2022, 3, 2, 19, 12)
      >>> get_next_monday(d)
      datetime.datetime(2022, 3, 7, 19, 12)

      >>> get_next_monday(d.date())
      datetime.date(2022, 3, 7)

      >>> get_previous_monday(d)
      datetime.datetime(2022, 2, 28, 19, 12)

      >>> get_previous_wednesday(d.date())
      datetime.date(2022, 2, 23)


.. autoclass:: flextime

.. autofunction:: daterange([start,] stop[, step])

.. autoclass:: DateField

.. autoclass:: TimeSpan

   .. automethod:: from_date
   .. automethod:: replace


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
   .. automethod:: replace

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
