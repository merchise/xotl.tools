- Moves SmartDict and SortedSmartDict from :mod:`xoutil.data` to
  :mod:`xoutil.collections`.

  They are still accessible from :mod:`!xoutil.data` but deprecated there.

  Also there is now a :class:`xoutil.collections.SmartDictMixin` that
  implements the `update` behind all smart dicts in xoutil.

- :class:`xoutil.collections.StackedDict` gains zero-level initialization data
  and is now a smart dict.

- Removed :func:`!xoutil.iterators.first`, and
  :func:`!xoutil.iterators.get_first`.

  Deprecates :func:`xoutil.iterators.obtain`.

  Introduces :func:`xoutil.iterators.first_non_null`.

- Adds :func:`xoutil.objects.copy_class` and updates
  :func:`xoutil.decorator.compat.metaclass` to use it.

- Fixes a bug with :func:`xoutil.deprecation.deprecated` when used with
  classes: It changed the hierarchy and provoked infinite recursion in methods
  that use `super`.
