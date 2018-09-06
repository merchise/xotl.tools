- With the release of 2.0.0, xoutil ends it support for Python 2.

  Releases 1.9 are a *continuation* of the 1.8 series and don't break any
  API found in the last release of that series: 1.8.8.

- Add `xoutil.objects.import_object`:func:.

- Add `xoutil.context.Context.from_defaults`:meth: and
  `xoutil.context.Context.from_dicts`:meth:.

- Deprecate imports from top-level `xoutil`:mod:.  The following objects
  should be imported from `xoutil.symbols`:mod:\ :

  .. hlist::
     :columns: 3

     - `~xoutil.symbols.Unset`:obj:
     - `~xoutil.symbols.Undefined`:obj:
     - `~xoutil.symbols.Invalid`:obj:
     - `~xoutil.symbols.Ignored`:obj:
