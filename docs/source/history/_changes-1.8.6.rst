- Fix bug `#24`_: `~xoutil.future.datetime.TimeSpan`:class: should always
  return a `datetime.date`:class: for its `start_date` and `end_date`
  attribute.  Even if initialized with `datetime.datetime`:class:

.. _#24: https://gitlab.lahavane.com/merchise/xoutil/issues/24
