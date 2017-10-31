This is the first of the 1.2.0 series. It's been given a bump in the minor
version number because we've removed some deprecated functions and/or modules.

- Several enhancements to `xoutil.string`:mod: to make it work on Python 2.7
  and Python 3.2.

  Deprecates `xoutil.string.normalize_to_str`:func: in favor of the newly
  created `xoutil.string.force_str`:func: which is Python 3 friendly.

- Backwards incompatible changes in `xoutil.objects`:mod: API. For instance,
  replaces `getattr` parameter with `getter` in `xoutil.objects.xdir`:func:
  and co.

- Extracts decorator-making facilities from `xoutil.decorators`:mod: into
  `xoutil.mdeco`:mod:.

  .. The decorator-making decorator
  .. `xoutil.mdeco.decorator`:func: returns a signature-keeping decorator.

- Fixes in `!xoutil.aop.extended`:mod:. Added parameters in
  `!xoutil.aop.classical.weave`:func:.

- Introduces `xoutil.iterators.first_n`:func: and deprecates
  `xoutil.iterators.first`:func: and `xoutil.iterators.get_first`:func:.

- Removes the `zope.interface` awareness from `xoutil.context`:mod: since it
  contained a very hard to catch bug. Furthermore, this was included to help
  the implementation of `xotl.ql`, and it's no longer used there.

  This breaks version control policy since it was not deprecated beforehand,
  but we feel it's needed to avoid spreading this bug.

- Removed long-standing deprecated modules `xoutil.default_dict`:mod:,
  `xoutil.memoize`:mod: and `xoutil.opendict`:mod:.

- Fixes bug in `xoutil.datetime.strfdelta`:func:.  It used to show things like
  '1h 62min'.

- Introduces `xoutil.compat.class_type`:data: that holds class types for Python
  2 or Python 3.
