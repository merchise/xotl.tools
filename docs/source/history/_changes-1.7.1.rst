- Add `xoutil.collections.PascalSet`:class: and
  `xoutil.collections.BitPascalSet`:class:.

- Add `xoutil.functools.lwraps`:func:.

- Add `xoutil.objects.multi_getter`:func:,
  `xoutil.objects.get_branch_subclasses`:func:,
  `xoutil.objects.fix_method_documentation`:func:.

- Add `xoutil.string.safe_str`:func:

- Remove long deprecated modules: `!xoutil.aop`:mod: and `!xoutil.proxy`:mod:.

- Deprecate ``xoutil.html`` entirely.

- The following modules are included on a *provisional basis*.  Backwards
  incompatible changes (up to and including removal of the module) may occur
  if deemed necessary by the core developers:

  - `xoutil.connote`:mod:.

  - `xoutil.params`:mod:.

Fixes in 1.7.1.post1:

- Fix issue with both `xoutil.string.safe_decode`:func: and
  `xoutil.string.safe_encode`:func:.

  Previously, the parameter encoding could contain an invalid encoding name
  and the function could fail.


Fixes in 1.7.1.post2:

- Fix `xoutil.string.cut_suffix`:func:. The following invariant was being
  violated::

    >>> cut_suffix(v, '') == v  # for any value of 'v'
