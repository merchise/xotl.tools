- Lots of removals.  Practically all deprecated since 1.4.0 (or before).  Let's
  list a few but not all:

  - Both `xoutil.Unset`:obj: and `xoutil.Ignored`:obj: are no longer
    re-exported in `xoutil.types`:mod:.

  - Removes module `!xoutil.decorator.compat`:mod:, since it only contained the
    deprecated decorator `!xoutil.decorator.compat.metaclass`:func: in favor of
    `xoutil.objects.metaclass`:func:.

  - Removes ``nameof`` and ``full_nameof`` from `xoutil.objects`:mod: in favor
    of `xoutil.names.nameof`:func:.

  - Removes ``pow_`` alias of `xoutil.functools.power`:func:.

  - Removes the deprecated ``xoutil.decorator.decorator`` function.  Use
    `xoutil.decorator.meta.decorator`:func: instead.

  - Now `~xoutil.modules.get_module_path`:func: is documented and in module
    `xoutil.modules`:mod:.

- Also we have documented a few more functions, including
  `xoutil.fs.path.rtrim`:func:.

- All modules below `!xoutil.aop`:mod: are in risk and are being deprecated.
