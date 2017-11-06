- Remove deprecated `xoutil.objects.get_and_del_first_of`:func:,
  `xoutil.objects.smart_getattr`:func:, and
  `xoutil.objects.get_and_del_attr`:func:.

- Remove deprecated arguments from `xoutil.objects.xdir`:func: and
  `xoutil.objects.fdir`:func:.

- Fix bug `#17`_: `xoutil.fp.tools.compose`:class: is not wrappable.

- Move `xoutil.decorator.memoized_property`:class: to
  `xoutil.objects.memoized_property`:class: module.  Deprecate the first.

.. _#17: https://gitlab.lahavane.com/merchise/xoutil/issues/17
