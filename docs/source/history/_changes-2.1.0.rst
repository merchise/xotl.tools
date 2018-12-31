- Repackage ``xoutil`` under `xotl.tools`:mod:.

- Remove deprecated module ``xoutil.logger``.

- Remove package ``xoutil.eight``.

- Remove deprecated functions and classes ``xoutil.future.inspect.type_name``,
  ``xoutil.future.functools.ctuple``, and ``xoutil.future.functools.compose``.

- Add `xotl.tools.deprecation.deprecated_alias`:func:.

- Allow to customize Quantity in `xotl.tools.dim.meta.Dimension`:class: and,
  by argument, in `~xotl.tools.dim.meta.Dimension.new`:meth:.

- Deprecate ``xoutil.future.itertools.zip()``, and
  ``xoutil.future.itertools.map()``.

- Re-implement `xotl.tools.future.itertools.merge`:func: in terms of
  `heapq.merge`:func:.

- Add `xotl.tools.tasking.get_backoff_wait`:func:
