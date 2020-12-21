- Implement `xotl.tools.objects.memoized_property`:class: using
  `functools.cached_property`:class: in Python 3.8+.

- Implement `xotl.tools.objects.classproperty`:any: by composing
  `classmethod`:any: and `property`:any: in Python 3.9+.

- Update `xotl.tools.modules.moduleproperty`:func: to call ``__set_name__`` on
  the base property if available.
