- Remove deprecated `xoutil.objects.get_and_del_first_of`:func:,
  `xoutil.objects.smart_getattr`:func:, and
  `xoutil.objects.get_and_del_attr`:func:.

- Remove deprecated arguments from `xoutil.objects.xdir`:func: and
  `xoutil.objects.fdir`:func:.

- Fix bug #17: `xoutil.fp.tools.compose`:class: is not wrappable.

- Move `xoutil.decorator.memoized_property`:class: to
  `xoutil.objects.memoized_property`:class: module.  Deprecate the first.

- Deprecate `xoutil.decorator.memoized_instancemethod`:class:.

- Deprecate `xoutil.decorator.reset_memoized`:func:.  Use
  `~xoutil.decorator.memoized_property.reset`:meth:.

- Fix bug (unregistered): `xoutil.objects.traverse`:func: ignores its
  `getter`.
