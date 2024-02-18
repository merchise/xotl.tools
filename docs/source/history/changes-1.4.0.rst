- Refactors ``xoutil.types`` as explained in ``types-140-refactor``.

- Changes involving ``xoutil.collections``\ :

  - Moves SmartDict and SortedSmartDict from ``xoutil.data`` to
    ``xoutil.collections``. They are still accessible from
    ``xoutil.data``.

  - Also there is now a ``xoutil.collections.SmartDictMixin`` that
    implements the `update` behind all smart dicts in xoutil.

  - ``xoutil.collections.StackedDict`` in now a SmartDict and thus gains
    zero-level initialization data.

- Removals of deprecated, poorly tested, or incomplete features:

  - Removes deprecated ``xoutil.decorators``.  Use
    ``xoutil.decorator``.

  - Removed ``xoutil.iterators.first``, and ``xoutil.iterators.get_first``.

  - Removed ``xoutil.string.names``, ``xoutil.string.normalize_to_str`` and
    ``xoutil.string.normalize_str_collection``.

- Newly deprecated functions:

  - Deprecates ``xoutil.iterators.obtain``.

  - Deprecates ``xoutil.iterators.smart_dict`` and
    `xoutil.data.smart_copy` in favor of ``xoutil.objects.smart_copy``.

- New features:

  - Introduces ``xoutil.iterators.first_non_null``.

  - Adds ``xoutil.objects.copy_class`` and updates
    ``xoutil.decorator.compat.metaclass`` to use it.

- Fixes a bug with ``xoutil.deprecation.deprecated`` when used with classes:
  It changed the hierarchy and provoked infinite recursion in methods that use
  ``super``.
