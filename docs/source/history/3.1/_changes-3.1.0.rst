.. rubric:: Packaging and distribution changes


- Ensure to run (non deprecated) doctests in the CI pipeline.

.. rubric:: Bug fixes

- Fix format of `xotl.tools.future.datetime.strfdelta`:func:.


.. rubric:: Removals and deprecations


- Deprecate module ``xotl.tools.records``.  Use modern alternatives like
  `pydantic`_.

- Deprecate functions `xotl.tools.decorator`:mod:\ :

  - ``xotl.tools.decorator.constant_bagger``
  - ``xotl.tools.decorator.aliases``
  - ``xotl.tools.decorator.settle``
  - ``xotl.tools.decorator.namer``
  - ``xotl.tools.decorator.AttributeAlias``
  - ``xotl.tools.decorator.assignment_operator``
  - ``xotl.tools.decorator.instantiate``
  - ``xotl.tools.decorator.singleton`` (undocumented)

- Remove deprecated modules:

  - ``xotl.tools.progress``
  - ``xotl.tools.web``


- Remove deprecated:

  - ``xotl.tools.decorator.memoized_instancemethod``
  - ``xotl.tools.decorator.reset_memoized``

.. _pydantic: https://pypi.org/project/pydantic/
.. _beartype: https://pypi.org/project/beartype/
