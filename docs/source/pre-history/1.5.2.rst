- Deprecated function ``xoutil.objects.get_and_del_key``.  Use the
  `dict.pop`:meth: directly.

  To have consistent naming, renamed ``xoutil.objects.get_and_del_attr`` and
  ``xoutil.objects.get_and_del_first_of`` to ``xoutil.objects.popattr`` and
  ``xoutil.objects.pop_first_of``.  Old names are left as deprecated aliases.

- Now ``xoutil.functools.update_wrapper``, ``xoutil.functools.wraps`` and
  ``xoutil.functools.lru_cache`` are Python 3.3 backports (or aliases).

- New module ``xoutil.textwrap``.
