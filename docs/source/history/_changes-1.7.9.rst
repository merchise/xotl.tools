- Deprecate ``xoutil.dim.meta.Signature.isunit``.

- Rename ``xoutil.dim.meta.QuantityType`` to
  ``xoutil.dim.meta.Dimension``.

- Fix bug__ in ``xoutil.datetime.TimeSpan``.
  ``xoutil.datetime.TimeSpan.start_date`` and
  ``xoutil.datetime.TimeSpan.end_date`` now return an instance of
  Python's `datetime.date`:class: instead of a sub-class.

__ https://github.com/merchise/xoutil/commit/9948d480da994212182ff7c4c865e8588e394952
