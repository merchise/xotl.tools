- Lots of removals.  Practically all deprecated since 1.4.0 (or before).  Let's
  list a few but not all:

  - Both :obj:`xoutil.Unset` and :obj:`xoutil.ignored` are no longer
    re-exported in :mod:`xoutil.types`.

  - Removes module :mod:`!xoutil.decorator.compat`, since it only contained the
    deprecated decorator :func:`!xoutil.decorator.compat.metaclass` in favor of
    :func:`xoutil.objects.metaclass`.
