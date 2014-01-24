- Adds :func:`xoutil.datetime.daterange`.

- Adds :func:`xoutil.objects.traverse`.

- Adds :func:`xoutil.fs.makedirs` and :func:`xoutil.fs.ensure_filename`

- The `fill` argument in function :func:`xoutil.iterators.slides` now
  defaults to None. This is consistent with the intended usage of
  :class:`~xoutil.Unset` and with the semantics of both
  :func:`xoutil.iterators.continuously_slides` and
  :func:`xoutil.iterators.first_n`.

  Unset, as a default value for parameters, is meant to signify the absence
  of an argument and thus only would be valid if an absent argument had some
  kind of effect *different* from passing the argument.

- Changes :func:`xoutil.modules.customize` API to separate options from
  custom attributes.

- Includes a `random` parameter to :func:`xoutil.uuid.uuid`.
