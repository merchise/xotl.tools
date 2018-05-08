- Fix `xoutil.eight.iteritems`:func:, `xoutil.eight.itervalues`:func: and
  `xoutil.eight.iterkeys`:func: to return an iterator.

- `~xoutil.validators.identifiers.is_valid_identifier`:func: so that it uses
  `str.isidentifier`:meth: in Python 3.

- Add class method `xoutil.future.collections.opendict.from_enum`:meth:
