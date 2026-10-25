.. rubric:: Removals

- Removed ``xotl.tools.names.namelist`` and ``strlist``, deprecated since 3.0.0.  Use ordinary
  lists, explicitly converting objects with ``nameof`` or ``str`` where needed.

- Removed ``xotl.tools.future.datetime.strftime``.  Call the standard-library ``date.strftime`` or
  ``datetime.strftime`` method on the value instead.

- Removed ``xotl.tools.params.check_default``, deprecated since 3.0.0.  Use an explicit optional
  parameter with a sentinel default, and positional-only syntax where appropriate.

- Removed ``xotl.tools.records`` and its field readers.  Use dataclasses or explicit parsing and
  validation of input records instead.

- Removed the ``xotl.tools.future.collections.defaultdict`` alias.  Use ``DefaultDict`` for the
  extended default factory protocol, or ``collections.defaultdict`` for the standard behavior.

- Removed ``xotl.tools.modules.copy_members``.  Use explicit imports and re-exports instead.

- Removed ``xotl.tools.modules.force_module``.  Pass module objects explicitly or use
  ``importlib.import_module`` for module names instead of inspecting the caller's stack.

- Removed ``xotl.tools.decorator``, including ``decorator.meta.decorator``.  Implement decorators
  as ordinary Python functions with explicit signatures and use ``functools.wraps`` as needed.

- Removed ``xotl.tools.values`` and its ``simple`` and ``ids`` submodules, including
  ``str_coerce`` and ``str_uuid``.  Use explicit validation and conversions, collection ABCs,
  and the standard ``uuid`` module instead.

- Removed ``xotl.tools.fp.prove`` and ``fp.prove.semantic``.  Use explicit validation,
  exception handling, and conversion instead.  The retained parameter-schema classes keep
  their coercion protocol through a private implementation, independent of the removed APIs.

- Removed ``xotl.tools.params.single`` after removing its proof-framework consumers.
  Use explicit argument-shape checks where needed.

.. rubric:: Changes

- Retained helpers no longer import ``xotl.tools.params``.  Their existing argument ordering
  and supported calling forms are preserved; required positional arguments are declared
  directly where possible, and genuine variadic constraints are validated locally.

- ``xotl.tools.bound.boundary`` no longer depends on the removed decorator factory.  Its bare,
  empty-parentheses, and positional or keyword configuration forms remain supported.

- `~xotl.tools.string.slugify`:func: remains supported and no longer depends on the deprecated
  parameter-schema and coercion helpers.  Its implementation now declares the documented parameters
  directly, using Python's native argument binding instead of manually parsing ``*args, **kwargs``.
  Use the documented names ``invalid_chars`` and ``valid_chars`` instead of the legacy aliases
  ``invalid`` and ``valid``.  Unknown keywords, excess positional arguments, and duplicate arguments
  now raise ``TypeError`` instead of being silently accepted.

.. rubric:: Deprecations

- Deprecate the entire `xotl.tools.clipping`:mod: module for removal in 4.0.0, including ``crop``,
  ``small``, ``short``, ``crop_iterator``, its constants, and the ``__crop__`` protocol.  Prefer
  `reprlib`:mod: for abbreviated object representations.  Existing clipping behavior is retained;
  migration requires reviewing output differences and reprlib features added in Python 3.11+.

.. rubric:: Retained deprecated APIs

- The ``xotl.tools.cli`` package remains available in 3.6.0.

- ``xotl.tools.params.ParamManager``, ``ParamSchemeRow``, and ``ParamScheme`` remain available until
  their announced removal in 4.0.0.
