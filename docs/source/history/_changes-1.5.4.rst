- Fix a bug in `xoutil.objects.extract_attrs`:func:.  It was not raising
  exceptions when some attribute was not found and `default` was not provided.

  Also now the function supports paths like
  `xoutil.objects.get_traverser`:func:.

- `xoutil` contains now a copy of the excellent project `six`_ exported as
  ``xoutil.six`` (not documented here).  Thus the compatibility module
  ``xoutil.compat`` is now deprecated and will removed in the future.

  There are some things that ``xoutil.compat`` has that ``xoutil.six`` does
  not.  For instance, ``six`` does not include fine grained python version
  markers.  So if your code depends not on Python 3 v Python 2 dichotomy but
  on features introduced in Python 3.2 you must use the ``sys.version_info``
  directly.

  Notwithstanding that, ``xoutil`` will slowly backport several Python 3.3
  standard library features to Python 2.7 so that they are consistently used
  in any Python up to 2.7 (but 3.0).

.. _six: https://pypi.python.org/pypi/six
