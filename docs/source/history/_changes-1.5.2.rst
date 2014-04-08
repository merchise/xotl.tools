- Deprecated function :func:`xoutil.objects.get_and_del_key`. Use the
  `dict.pop`:meth: directly.

  To have consistent naming, renamed :func:`~xoutil.objects.get_and_del_attr`
  and :func:`~xoutil.objects.get_and_del_first_of` to
  :func:`~xoutil.objects.popattr` and :func:`~xoutil.objects.pop_first_of`.
  Old names are left as deprecated aliases.

- Now :func:`xoutil.functools.update_wrapper`, :func:`xoutil.functools.wraps`
  and :func:`xoutil.functools.lru_cache` are Python 3.3 backports (or
  aliases).

- New module :mod:`xoutil.textwrap`.
