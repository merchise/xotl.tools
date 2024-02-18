.. rubric:: Deprecations and introductions:

- Importing ``xoutil.Unset`` and ``xoutil.Ignored`` from ``xoutil.types``
  now issues a warning.

- New style for declaring portable metaclasses in
  ``xoutil.objects.metaclass``, so ``xoutil.decorator.compat.metaclass`` is
  now deprecated.

- Adds the module ``xoutil.pprint`` and function ``xoutil.pprint.ppformat``.

- Adds the first version of package ``xoutil.cli``.

- Adds the `filter` parameter to functions ``xoutil.objects.xdir`` and
  ``xoutil.objects.fdir`` and deprecates `attr_filter` and `value_filter`.

- Adds functions ``xoutil.objects.attrclass``, ``xoutil.objects.fulldir``.

- Adds function ``xoutil.iterators.continuously_slides``.

- Adds package ``xoutil.threading``.

- Adds package ``xoutil.html`` module and begins the port of
  ``xoutil.html.parser`` from Python 3.3 to xoutil, so that a common
  implementation for both Python 2.7 and Python 3.3 is available.

.. rubric:: Bug fixes:

- Fixes some errors with classical AOP weaving of functions in modules that
  where customized.

- Fixes bugs with ``xoutil.modules``: makes ``xoutil.modules.modulemethod`` to
  customize the module, and improves performance.
