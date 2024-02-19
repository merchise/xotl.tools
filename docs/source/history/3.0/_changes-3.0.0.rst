.. rubric:: Packaging and distribution changes

- No longer distribute the package 'xoutil'.

- No longer keep re-exporting all symbols from the standard library.

- Add support for Python 3.11 and Python 3.12, drop support for Python 3.7.

  This means we now include Python 3.11, 3.12 in our CI tests and no longer
  test with 3.7.

  The list of supported Python versions is: 3.8, 3.9, 3.10, 3.11, and 3.12.

.. rubric:: General changes (mostly backwards-compatible)

- Make `xotl.tools.objects.classproperty`:class: work again in Python 3.11.

- Make 'default' positional-only argument in
  `xotl.tools.future.inspect.get_attr_value`:func:.


.. rubric:: Possibly backwards-incompatible changes (excluding removals).

- Change the signature of `xotl.tools.objects.copy_class`:func: to take
  keyword-only arguments.

.. rubric:: Removals and deprecations

- Deprecate `xotl.tools.names.namelist`:class:, and
  `xotl.tools.names.strlist`:class:.

- Deprecate the module `xotl.tools.deprecation`:mod:, and removed deprecated
  ``xotl.tools.deprecation.deprecated_alias``.  Instead you should use the
  upcoming `warnings.deprecated`:func: (or
  `typing_extensions.deprecated`:func:).

  This library no longer uses this module for deprecation.

- Deprecate function `xotl.tools.modules.copy_members`:func:, this was mainly
  an internal function to provide the drop-in replacement of standard library
  modules.

- Deprecate function `xotl.tools.modules.force_module`:func:, this was mainly
  an internal function for the (now deprecated) module
  ``xotl.tools.deprecation``.

- Deprecate function `xotl.tools.modules.get_module_path`:func:.  This is not
  portable, and can fail for extensions, etc.

- Deprecate param-related utitilies for which there are now better syntactical
  approaches:

  - `xotl.tools.params.check_default`:func:
  - `xotl.tools.params.single`:func:
  - `xotl.tools.params.ParamManager`:class:
  - `xotl.tools.params.ParamSchemeRow`:class:
  - `xotl.tools.params.ParamScheme`:class:

- Remove old backports or aliases:

  - ``xotl.tools.future.itertools.merge``
  - ``xotl.tools.future.itertools.zip``
  - ``xotl.tools.future.itertools.zip_longest``
  - ``xotl.tools.future.itertools.map``

  - ``xotl.tools.future.collections.ChainMap``
  - ``xotl.tools.future.collections.Counter``
  - ``xotl.tools.future.types.SimpleNamespace``
  - ``xotl.tools.future.types.DynamicClassAttribute``

- Remove deprecated modules:

  - ``xotl.tools.future.contextlib``
  - ``xotl.tools.future.time``

- Remove deprecated methods ``pop`` and ``push`` of
  `xotl.tools.future.collections.StackedDict`:class:.

- Remove deprecated ``xotl.tools.tasking.StandardWait``.

- Remove undocumented module ``xotl.tools.versions`` (use
  `packaging.versions`:mod:).

- Remove undocumented module ``xotl.tools.tools``.
