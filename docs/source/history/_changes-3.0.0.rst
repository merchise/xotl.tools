- No longer distribute the package 'xoutil'.

- Add support for Python 3.11 and Python 3.12, drop support for Python 3.7.
  This means we now include Python 3.11, 3.12 in our CI tests and no longer
  test with 3.7.

- Make `xotl.tools.objects.classproperty`:any: work again in Python 3.11.

- Use `DeprecationWarning`:class: in `xotl.tools.deprecation`:mod:.
