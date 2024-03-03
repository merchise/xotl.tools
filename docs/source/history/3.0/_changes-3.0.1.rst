.. rubric:: Fixes and non-breaking changes

- Fix `ImportError` while calling `xotl.tools.future.functools.curry`:func:.

- Ensure to run (non deprecated) doctests in the CI pipeline.

.. rubric:: Removals and deprecations

- New deprecations in `xotl.tools.decorator`:mod:\ :

  - ``xotl.tools.decorator.constant_bagger``
  - ``xotl.tools.decorator.aliases``
  - ``xotl.tools.decorator.settle``
  - ``xotl.tools.decorator.namer``
  - ``xotl.tools.decorator.AttributeAlias``
  - ``xotl.tools.decorator.assignment_operator``
  - ``xotl.tools.decorator.instantiate``
  - ``xotl.tools.decorator.singleton`` (undocumented)

- Remove deprecated:

  - ``xotl.tools.decorator.memoized_instancemethod``
  - ``xotl.tools.decorator.reset_memoized``
