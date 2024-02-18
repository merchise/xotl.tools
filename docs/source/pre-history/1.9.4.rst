- Fix ``xoutil.eight.iteritems``, ``xoutil.eight.itervalues`` and
  ``xoutil.eight.iterkeys`` to return an iterator.

- ``xoutil.validators.identifiers.is_valid_identifier`` so that it uses
  `str.isidentifier`:meth: in Python 3.

- Add class method ``xoutil.future.collections.opendict.from_enum``
