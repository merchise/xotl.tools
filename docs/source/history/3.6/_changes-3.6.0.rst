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

.. rubric:: Changes

- `~xotl.tools.string.slugify`:func: remains supported and no longer depends on the deprecated
  parameter-schema and coercion helpers.  Its implementation now declares the documented parameters
  directly, using Python's native argument binding instead of manually parsing ``*args, **kwargs``.
  Use the documented names ``invalid_chars`` and ``valid_chars`` instead of the legacy aliases
  ``invalid`` and ``valid``.  Unknown keywords, excess positional arguments, and duplicate arguments
  now raise ``TypeError`` instead of being silently accepted.

.. rubric:: Retained deprecated APIs

- The ``xotl.tools.cli`` package remains available in 3.6.0.

- ``xotl.tools.params.ParamManager``, ``ParamSchemeRow``, and ``ParamScheme`` remain available until
  their announced removal in 4.0.0.
