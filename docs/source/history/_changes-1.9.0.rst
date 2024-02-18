- With the release of 2.0.0, xoutil ends it support for Python 2.

  Releases 1.9 are a *continuation* of the 1.8 series and don't break any
  API found in the last release of that series: 1.8.8.

- Add ``xoutil.objects.import_object``.

- Add ``xoutil.context.Context.from_defaults`` and
  ``xoutil.context.Context.from_dicts``.

- Deprecate imports from top-level ``xoutil``.  The following objects
  should be imported from ``xoutil.symbols``\ :

  .. hlist::
     :columns: 3

     - ``xoutil.symbols.Unset``
     - ``xoutil.symbols.Undefined``
     - ``xoutil.symbols.Invalid``
     - ``xoutil.symbols.Ignored``
