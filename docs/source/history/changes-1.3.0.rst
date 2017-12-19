- Removes deprecated module `!xoutil.mdeco`:mod:.

- `xoutil.context.Context`:class: now inherit from the newly created stacked
  dict class `xoutil.collections.StackedDict`:class:. Whenever you enter a
  context a new level of the stacked dict is `pushed
  <xoutil.collections.StackedDict.push>`:meth:, when you leave the context a
  level is <xoutil.collections.StackedDict.pop>`:meth:.

  This also **removes** the `data` attribute execution context used to have,
  and, therefore, this is an incompatible change.

- Introduces `xoutil.collections.OpenDictMixin`:class: and
  `xoutil.collections.StackedDict`:class:.

- Fixes a bug in `xoutil.decorator.compat.metaclass`:func:\ : Slots were not
  properly handed.

- Fixes a bug with the simple `xoutil.collections.opendict`:class: that allowed
  to shadow methods (even `__getitem__`) thus making the dict unusable.
