.. rubric:: New

- Add module `xotl.tools.testing.unit`:mod:.

- Add methods `TimeSpan.replace
  <xotl.tools.future.datetime.TimeSpan.replace>`:any:, and
  `DateTimeSpan.replace <xotl.tools.future.datetime.DateTimeSpan.replace>`:any:.

.. rubric:: Typing changes

- The symbols in `xotl.tools.symbols`:mod: are casted to `typing.Any`:any:.


.. rubric:: Bug fixes

- Fix bug with `~xotl.tools.future.datetime.EmptyTimeSpan`:data: ``__gt__``.

  The following invariant should be false for any `time span
  <xotl.tools.future.datetime.TimeSpan>`:class: but it was returning true::

      EmptyTimeSpan > tspan

- Fix bug in `~xotl.tools.future.datetime.strfdelta`:func: when the timedelta
  has days.
