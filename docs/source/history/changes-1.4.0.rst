- Refactors :mod:`xoutil.types` as explained in :ref:`types-140-refactor`.

- Changes involving :mod:`xoutil.collections`:

  - Moves SmartDict and SortedSmartDict from :mod:`xoutil.data` to
    `xoutil.collections`:mod:. They are still accessible from
    `!xoutil.data`:mod:.

  - Also there is now a :class:`xoutil.collections.SmartDictMixin` that
    implements the `update` behind all smart dicts in xoutil.

  - :class:`xoutil.collections.StackedDict` in now a SmartDict and thus gains
    zero-level initialization data.

- Removals of deprecated, poorly tested, or incomplete features:

  - Removes deprecated :mod:`!xoutil.decorators`. Use :mod:`xoutil.decorator`.

  - Removed :func:`!xoutil.iterators.first`, and
    :func:`!xoutil.iterators.get_first`.

  - Removed :func:`!xoutil.string.names`, :func:`!xoutil.string.normalize_to_str`
    and :func:`!xoutil.string.normalize_str_collection`.

- Newly deprecated functions:

  - Deprecates :func:`xoutil.iterators.obtain`.

  - Deprecates :func:`xoutil.iterators.smart_dict` and
    :func:`xoutil.data.smart_copy` in favor of :func:`xoutil.objects.smart_copy`.

- New features:

  - Introduces :func:`xoutil.iterators.first_non_null`.

  - Adds :func:`xoutil.objects.copy_class` and updates
    :func:`xoutil.decorator.compat.metaclass` to use it.

- Fixes a bug with :func:`xoutil.deprecation.deprecated` when used with
  classes: It changed the hierarchy and provoked infinite recursion in methods
  that use `super`.
