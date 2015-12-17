- Lots of removals.  Practically all deprecated since 1.4.0 (or before).  Let's
  list a few but not all:

  - Both :obj:`xoutil.Unset` and :obj:`xoutil.Ignored` are no longer
    re-exported in :mod:`xoutil.types`.

  - Removes module :mod:`!xoutil.decorator.compat`, since it only contained the
    deprecated decorator :func:`!xoutil.decorator.compat.metaclass` in favor of
    :func:`xoutil.objects.metaclass`.

  - Removes ``nameof`` and ``full_nameof`` from :mod:`xoutil.objects` in favor
    of :func:`xoutil.names.nameof`.

  - Removes ``pow_`` alias of :func:`xoutil.functools.power`.

  - Removes the deprecated ``xoutil.decorator.decorator`` function.  Use
    :func:`xoutil.decorator.meta.decorator` instead.

  - Now :func:`~xoutil.modules.get_module_path` is documented and in module
    :mod:`xoutil.modules`.

- Also we have documented a few more functions, including
  :func:`xoutil.fs.path.rtrim`.

- All modules below :mod:`!xoutil.aop` are in risk and are being deprecated.
