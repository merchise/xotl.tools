This is the first of the 1.2.0 series. It's been given a bump in the minor
version number because we've removed some deprecated functions and/or modules.

- Several enhancements to :mod:`xoutil.string` to make it work on Python 2.7
  and Python 3.2.

  Deprecates :func:`xoutil.string.normalize_to_str` in favor of the newly
  created :func:`xoutil.string.force_str` which is Python 3 friendly.

- Backwards incompatible changes in :mod:`xoutil.objects` API. For instance,
  replaces `getattr` parameter with `getter` in :func:`xoutil.objects.xdir` and
  co.

- Extracts decorator-making facilities from :mod:`xoutil.decorators` into
  :mod:`xoutil.mdeco`.

  .. The decorator-making decorator
  .. :func:`xoutil.mdeco.decorator` returns a signature-keeping decorator.

- Fixes in :mod:`!xoutil.aop.extended`. Added parameters in
  :func:`!xoutil.aop.classical.weave`.

- Introduces :func:`xoutil.iterators.first_n` and deprecates
  :func:`xoutil.iterators.first` and :func:`xoutil.iterators.get_first`.

- Removes the `zope.interface` awareness from :mod:`xoutil.context` since it
  contained a very hard to catch bug. Furthermore, this was included to help
  the implementation of `xotl.ql`, and it's no longer used there.

  This breaks version control policy since it was not deprecated beforehand,
  but we feel it's needed to avoid spreading this bug.

- Removed long-standing deprecated modules :mod:`xoutil.default_dict`,
  :mod:`xoutil.memoize` and :mod:`xoutil.opendict`.

- Fixes bug in :func:`xoutil.datetime.strfdelta`. It used to show things like
  '1h 62min'.

- Introduces :data:`xoutil.compat.class_type` that holds class types for Python
  2 or Python 3.
