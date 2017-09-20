- Deprecate `xoutil.dim.meta.Signature.isunit`:meth:.

- Rename `xoutil.dim.meta.QuantityType`:class: to
  `xoutil.dim.meta.Dimension`:class:.

- Fix bug__ in `xoutil.datetime.TimeSpan`:class:.
  `~xoutil.datetime.TimeSpan.start_date`:attr: and
  `~xoutil.datetime.TimeSpan.end_date`:attr: now return an instance of
  Python's `datetime.date`:class: instead of a sub-class.

__ https://github.com/merchise/xoutil/commit/9948d480da994212182ff7c4c865e8588e394952
