- No longer distribute the package 'xoutil'.

- No longer keep re-exporting all symbols from the standard library.

- Add support for Python 3.11 and Python 3.12, drop support for Python 3.7.

  This means we now include Python 3.11, 3.12 in our CI tests and no longer
  test with 3.7.

  The list of supported Python versions is: 3.8, 3.9, 3.10, 3.11, and 3.12.

- Make `xotl.tools.objects.classproperty`:class: work again in Python 3.11.

- Use `DeprecationWarning`:class: in `xotl.tools.deprecation`:mod:.

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

- Remove undocumented module ``xotl.tools.versions``.
