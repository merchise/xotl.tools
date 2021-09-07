- Drop support for Python 3.5, 3.6 and 3.7 and commit to support Python 3.8,
  and 3.9.

  The code might run in Python 3.6+, but we're not testing anymore on those
  versions.


- Remove long-deprecated functions and classes:

  - `!xotl.tools.deprecation.inject_deprecated`:func:,
  - `!xotl.tools.future.types.is_module`:func:,
  - `!xotl.tools.future.types.are_instances`:func:,
  - `!xotl.tools.future.types.no_instances`:func:,
  - `!xotl.tools.decorator.meta.flat_decorator`:func:,
  - `!xotl.tools.cpystack.iter_frames`:func:,
  - `!xotl.tools.future.types.mro_dict`:class:,
  - `!xotl.tools.future.types.mro_get_value_list`:func:,
  - `!xotl.tools.future.types.mro_get_full_mapping`:func:,
  - `!xotl.tools.future.types.is_iterable`:func:,
  - `!xotl.tools.future.types.is_collection`:func:,
  - `!xotl.tools.future.types.is_mapping`:func:,
  - `!xotl.tools.future.types.is_string_like`:func:, and
  - `!xotl.tools.future.types.is_scalar`:func:.
