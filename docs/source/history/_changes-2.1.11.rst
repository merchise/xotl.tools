This release marks the last release of the series of 2.1.x.  We simply don't
have the manpower to keep many branches at the same time.

- Implement `xotl.tools.objects.memoized_property`:class: using
  `functools.cached_property`:class: in Python 3.8+.

- Implement `xotl.tools.objects.classproperty`:any: by composing
  `classmethod`:any: and `property`:any: in Python 3.9+.

- Update `xotl.tools.modules.moduleproperty`:func: to call ``__set_name__`` on
  the base property if available.

- Comparing quantities of different dimensions (`xotl.tools.dim`:mod:) no
  longer raises a TypeError, but returns NotImplemented.

  For ``==`` this means that Python will return False.  For other comparison
  operators (``<``, ``<=``, etc.), if Python cannot reverse the operation, it
  raises a TypeError.

- Deprecates module `xotl.tools.cli`:mod:.  This module hasn't been maintained
  for long and there are better alternatives in out there (e.g click_).

- Correct the name of `xotl.tools.dim.base.Pressure`:any:, previously it was
  mistyped missing as ``Presure``.

.. _click: https://click.palletsprojects.com/
