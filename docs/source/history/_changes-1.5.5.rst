- UserList are now collections in the sense of ``xoutil.types.is_collection``.

- Python 3.4 added to the list of tested Python environments.  Notice this
  does not makes any warrants about identical behavior of things that were
  previously backported from Python 3.3.

  For instance, the ``xoutil.collections.ChainMap`` has been already
  backported from Python 3.4, so it will have the same signature and behavior
  across all supported Python versions.

  But other new things in Python 3.4 are not yet backported to xoutil.

- Now ``xoutil.objects.metaclass`` supports the ``__prepare__`` classmethod of
  metaclasses.  This is fully supported in Python 3.0+ and partially mocked in
  Python 2.7.

- Backported ``xoutil.types.MappingProxyType`` from Python 3.3.

- Backported ``xoutil.types.SimpleNamespace`` from Python 3.4.

- Backported ``xoutil.types.DynamicClassAttribute`` from Python 3.4

- Added function ``xoutil.iterators.delete_duplicates``.

- Added parameter `ignore_underscore` to ``xoutil.string.normalize_slug``

- Added module ``xoutil.crypto`` with a function for generating passwords.

- Fixed several bug in ``xoutil.functools.compose``

- Makes ``xoutil.fs.path.rtrim`` have a default value for the amount of step
  to traverse.
