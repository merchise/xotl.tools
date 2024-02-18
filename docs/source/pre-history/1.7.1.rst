- Add ``xoutil.collections.PascalSet`` and
  ``xoutil.collections.BitPascalSet``.

- Add ``xoutil.functools.lwraps``.

- Add ``xoutil.objects.multi_getter``,
  ``xoutil.objects.get_branch_subclasses``,
  ``xoutil.objects.fix_method_documentation``.

- Add ``xoutil.string.safe_str``

- Remove long deprecated modules: ``xoutil.aop`` and ``xoutil.proxy``.

- Deprecate ``xoutil.html`` entirely.

- The following modules are included on a *provisional basis*.  Backwards
  incompatible changes (up to and including removal of the module) may occur
  if deemed necessary by the core developers:

  - ``xoutil.connote``.

  - ``xoutil.params``.

Fixes in 1.7.1.post1:

- Fix issue with both ``xoutil.string.safe_decode`` and
  ``xoutil.string.safe_encode``.

  Previously, the parameter encoding could contain an invalid encoding name
  and the function could fail.


Fixes in 1.7.1.post2:

- Fix ``xoutil.string.cut_suffix``. The following invariant was being
  violated::

    >>> cut_suffix(v, '') == v  # for any value of 'v'
