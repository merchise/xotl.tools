- Fixes some errors with :mod:`classical <xoutil.aop.classical>` AOP weaving of
  functions in modules that where :func:`customized
  <xoutil.modules.customize>`.

- Importing :data:`xoutil.Unset` and :data:`xoutil.Ignored` from
  :mod:`xoutil.types` now issues a warning.

- New style for declaring portable metaclasses in
  :func:`xoutil.objects.metaclass`, so
  :func:`xoutil.decorator.compat.metaclass` is now deprecated.

- Adds the module :mod:`xoutil.pprint` and function
  :func:`xoutil.pprint.ppformat`.
