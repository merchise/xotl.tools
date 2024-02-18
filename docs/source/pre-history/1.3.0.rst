- Removes deprecated module ``xoutil.mdeco``.

- ``xoutil.context.Context`` now inherit from the newly created stacked dict
  class ``xoutil.collections.StackedDict``. Whenever you enter a context a new
  level of the stacked dict is pushed, when you leave the context a level is
  ``xoutil.collections.StackedDict.pop``.

  This also **removes** the `data` attribute execution context used to have,
  and, therefore, this is an incompatible change.

- Introduces ``xoutil.collections.OpenDictMixin`` and
  ``xoutil.collections.StackedDict``.

- Fixes a bug in ``xoutil.decorator.compat.metaclass``\ : Slots were not
  properly handed.

- Fixes a bug with the simple ``xoutil.collections.opendict`` that allowed
  to shadow methods (even `__getitem__`) thus making the dict unusable.
