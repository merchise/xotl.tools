- Lots of removals.  Practically all deprecated since 1.4.0 (or before).  Let's
  list a few but not all:

  - Both ``xoutil.Unset`` and ``xoutil.Ignored`` are no longer
    re-exported in ``xoutil.types``.

  - Removes module ``xoutil.decorator.compat``, since it only contained the
    deprecated decorator ``xoutil.decorator.compat.metaclass`` in favor of
    ``xoutil.objects.metaclass``.

  - Removes ``nameof`` and ``full_nameof`` from ``xoutil.objects`` in favor
    of ``xoutil.names.nameof``.

  - Removes ``pow_`` alias of ``xoutil.functools.power``.

  - Removes the deprecated ``xoutil.decorator.decorator`` function.  Use
    ``xoutil.decorator.meta.decorator`` instead.

  - Now ``xoutil.modules.get_module_path`` is documented and in module
    ``xoutil.modules``.

- Also we have documented a few more functions, including
  ``xoutil.fs.path.rtrim``.

- All modules below ``xoutil.aop`` are in risk and are being deprecated.
