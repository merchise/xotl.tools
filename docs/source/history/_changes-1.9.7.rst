- Add support for Python 3.7.

- ``xoutil.eight.abc.ABC`` is an alias to the stdlib's `ABC` class if using
  Python 3.4+.

- Rename ``xoutil.fp.iterators.iter_compose`` to
  `xoutil.fp.iterators.kleisli_compose`:func:.  Leave ``iter_compose`` as
  deprecated alias.

- Add `xoutil.future.datetime.TimeSpan.diff`:meth:

- Add `xoutil.future.datetime.DateTimeSpan`:class:.
