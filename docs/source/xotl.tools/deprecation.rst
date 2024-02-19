`xotl.tools.deprecation`:mod: - Utils for marking deprecated elements
=====================================================================

.. automodule:: xotl.tools.deprecation

.. deprecated:: 3.0.0

   This module is now deprecated in favor of Python's 3.13
   `warnings.deprecated`:func: (or `typing_extensions.deprecated`:func:).

.. autofunction:: deprecated(replacement, msg=None, deprecated_module=None, removed_in_version=None, check_version=False)

.. autofunction:: import_deprecated

.. autofunction:: deprecate_module

.. autofunction:: deprecate_linked
