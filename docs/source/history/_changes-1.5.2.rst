- Deprecated function `xoutil.objects.get_and_del_key`:func:.  Use the
  `dict.pop`:meth: directly.

  To have consistent naming, renamed `~xoutil.objects.get_and_del_attr`:func:
  and `~xoutil.objects.get_and_del_first_of`:func: to
  `~xoutil.objects.popattr`:func: and `~xoutil.objects.pop_first_of`:func:.
  Old names are left as deprecated aliases.

- Now `xoutil.functools.update_wrapper`:func:, `xoutil.functools.wraps`:func:
  and `xoutil.functools.lru_cache`:func: are Python 3.3 backports (or
  aliases).

- New module `xoutil.textwrap`:mod:.
