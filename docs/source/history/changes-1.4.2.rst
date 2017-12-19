- Adds `xoutil.datetime.daterange`:func:.

- Adds `xoutil.objects.traverse`:func:.

- Adds `xoutil.fs.makedirs`:func: and `xoutil.fs.ensure_filename`:func:.

- The `fill` argument in function `xoutil.iterators.slides`:func: now defaults
  to None. This is consistent with the intended usage of
  `~xoutil.Unset`:class: and with the semantics of both
  `xoutil.iterators.continuously_slides`:func: and
  `xoutil.iterators.first_n`:func:.

  Unset, as a default value for parameters, is meant to signify the absence
  of an argument and thus only would be valid if an absent argument had some
  kind of effect *different* from passing the argument.

- Changes `xoutil.modules.customize`:func: API to separate options from
  custom attributes.

- Includes a `random` parameter to `xoutil.uuid.uuid`:func:.
