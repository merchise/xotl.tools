- Removes deprecated module :mod:`!xoutil.mdeco`.

- :class:`xoutil.context.Context` now inherit from the newly created stacked
  dict class :class:`xoutil.collections.StackedDict`. Whenever you enter a
  context a new level of the stacked dict is :meth:`pushed
  <xoutil.collections.StackedDict.push>`, when you leave the context a level is
  :meth:`poped <xoutil.collections.StackedDict.pop>`.

  This also **removes** the `data` attribute execution context used to have,
  and, therefore, this is an incompatible change.

- Introduces :class:`xoutil.collections.OpenDictMixin` and
  :class:`xoutil.collections.StackedDict`.

- Fixes a bug in :func:`xoutil.decorator.compat.metaclass`: Slots were not
  properly handed.

- Fixes a bug with the simple :class:`xoutil.collections.opendict` that allowed
  to shadow methods (even `__getitem__`) thus making the dict unusable.
