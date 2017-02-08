- UserList are now collections in the sense of
  `xoutil.types.is_collection`:func:.

- Python 3.4 added to the list of tested Python environments.  Notice this
  does not makes any warrants about identical behavior of things that were
  previously backported from Python 3.3.

  For instance, the `xoutil.collections.ChainMap`:class: has been already
  backported from Python 3.4, so it will have the same signature and behavior
  across all supported Python versions.

  But other new things in Python 3.4 are not yet backported to xoutil.

- Now `xoutil.objects.metaclass`:func: supports the ``__prepare__``
  classmethod of metaclasses.  This is fully supported in Python 3.0+ and
  partially mocked in Python 2.7.

- Backported `xoutil.types.MappingProxyType`:class: from Python 3.3.

- Backported `xoutil.types.SimpleNamespace`:class: from Python 3.4.

- Backported `xoutil.types.DynamicClassAttribute`:class: from Python 3.4

- Added function `xoutil.iterators.delete_duplicates`:func:.

- Added parameter `ignore_underscore` to `xoutil.string.normalize_slug`:func:.

- Added module `xoutil.crypto`:mod: with a function for generating passwords.

- Fixed several bug in `xoutil.functools.compose`:func:.

- Makes `xoutil.fs.path.rtrim`:func: have a default value for the amount of
  step to traverse.
