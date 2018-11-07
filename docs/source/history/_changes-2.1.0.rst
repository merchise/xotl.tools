- Remove package ``xoutil.eight``.

- Remove deprecated function ``xoutil.future.inspect.type_name``.

- Add `xoutil.deprecation.deprecated_alias`:func:.

- Allow to customize Quantity in `xoutil.dim.meta.Dimension`:class: and, by
  argument, in `~xoutil.dim.meta.Dimension.new`:meth:.

- Deprecate ``xoutil.future.itertools.zip()``, and
  ``xoutil.future.itertools.map()``.

- Re-implement `xoutil.future.itertools.merge`:func: in terms of
  `heapq.merge`:func:.

- Add `xoutil.tasking.get_backoff_wait`:func:
