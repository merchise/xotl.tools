- Remove deprecated ``xoutil.objects.get_and_del_first_of``,
  ``xoutil.objects.smart_getattr``, and ``xoutil.objects.get_and_del_attr``.

- Remove deprecated arguments from ``xoutil.objects.xdir`` and
  ``xoutil.objects.fdir``.

- Fix bug #17: ``xoutil.fp.tools.compose`` is not wrappable.

- Move ``xoutil.decorator.memoized_property`` to
  ``xoutil.objects.memoized_property`` module.  Deprecate the first.

- Deprecate ``xoutil.decorator.memoized_instancemethod``.

- Deprecate ``xoutil.decorator.reset_memoized``.  Use
  ``xoutil.decorator.memoized_property.reset``.

- Fix bug (unregistered): ``xoutil.objects.traverse`` ignores its `getter`.
