.. rubric:: New

- Add module `xotl.tools.testing.unit`:mod:.

.. rubric:: Bug fixes

- Fix bug with `~xotl.tools.future.datetime.EmptyTimeSpan`:data: ``__gt__``.

  The following invariant should be false for any `time span
  <xotl.tools.future.datetime.TimeSpan>`:class: but it was returning true::

      EmptyTimeSpan > tspan

- Fix bug in `~xotl.tools.future.datetime.strfdelta`:func: when the timedelta
  has days.
