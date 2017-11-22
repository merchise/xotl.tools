- Refactors `xoutil.types`:mod: as explained in ``types-140-refactor``.

- Changes involving `xoutil.collections`:mod:\ :

  - Moves SmartDict and SortedSmartDict from `xoutil.data`:mod: to
    `xoutil.collections`:mod:. They are still accessible from
    `!xoutil.data`:mod:.

  - Also there is now a `xoutil.collections.SmartDictMixin`:class: that
    implements the `update` behind all smart dicts in xoutil.

  - `xoutil.collections.StackedDict`:class: in now a SmartDict and thus gains
    zero-level initialization data.

- Removals of deprecated, poorly tested, or incomplete features:

  - Removes deprecated `!xoutil.decorators`:mod:.  Use
    `xoutil.decorator`:mod:.

  - Removed `!xoutil.iterators.first`:func:, and
    `!xoutil.iterators.get_first`:func:.

  - Removed `!xoutil.string.names`:func:,
    `!xoutil.string.normalize_to_str`:func: and
    `!xoutil.string.normalize_str_collection`:func:.

- Newly deprecated functions:

  - Deprecates `xoutil.iterators.obtain`:func:.

  - Deprecates `xoutil.iterators.smart_dict`:func: and
    `xoutil.data.smart_copy` in favor of `xoutil.objects.smart_copy`:func:.

- New features:

  - Introduces `xoutil.iterators.first_non_null`:func:.

  - Adds `xoutil.objects.copy_class`:func: and updates
    `xoutil.decorator.compat.metaclass`:func: to use it.

- Fixes a bug with `xoutil.deprecation.deprecated`:func: when used with
  classes: It changed the hierarchy and provoked infinite recursion in methods
  that use `super`.
