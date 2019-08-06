- Repackage ``xoutil`` under `xotl.tools`:mod:.  You can still import from the
  `xoutil namespace<xoutil>`:mod:.

- Remove deprecated module ``xoutil.logger``.

- Remove package ``xoutil.eight``.

- Remove deprecated ``xoutil.decorator.memoized_property``, use
  `xotl.tools.objects.memoized_property`:class:.

- Remove deprecated functions and classes ``xoutil.future.inspect.type_name``,
  ``xoutil.future.functools.ctuple``, and ``xoutil.future.functools.compose``.

- Remove deprecated top-level imports: ``xoutil.Unset``, ``xoutil.Undefined``,
  ``xoutil.Ignored`` and ``xoutil.Invalid``.

- Add `xotl.tools.deprecation.deprecated_alias`:func:.

- Allow to customize Quantity in `xotl.tools.dim.meta.Dimension`:class: and,
  by argument, in `~xotl.tools.dim.meta.Dimension.new`:meth:.

- Deprecate ``xoutil.future.itertools.zip()``, and
  ``xoutil.future.itertools.map()``.

- Re-implement `xotl.tools.future.itertools.merge`:func: in terms of
  `heapq.merge`:func:.

- Add `xotl.tools.tasking.get_backoff_wait`:func:

- Add `xotl.tools.objects.iter_final_subclasses`:func:,
  `xotl.tools.objects.get_final_subclasses`:func: and
  `xotl.tools.objects.FinalSubclassEnumeration`:func:.

- Deprecate module ``xotl.tools.progress``.

- Deprecate module ``xotl.tools.values.ids``.

- Deprecate ``xotl.tools.web.slugify``; use `xotl.tools.strings.slugify`:func:
  instead.

- Remove deprecated module ``xotl.tools.uuid``.

- Remove deprecated module ``xotl.tool.logical``.

- Remove deprecated module ``xotl.tools.formatter``.

- Remove deprecated function ``xotl.tools.tools.get_default``.
