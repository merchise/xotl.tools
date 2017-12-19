This release was mainly focused in providing a new starting point for several
other changes.  This release is being synchronized with the last release of
the 1.6.11 to allow deprecation messages to be included properly.

The following is the list of changes:

- The `defaults` `xoutil.objects.smart_copy`:func: has being made keyword
  only.

- Deprecates the `~xoutil.collections.StackedDict.pop`:meth: semantics, they
  shadow the `dict.pop`:func:.  A new
  `~xoutil.collections.StackedDict.pop_level`:meth: is provided to explicitly
  pop a stack level.  The same is done for the
  `~xoutil.collections.StackedDict.pop`:meth: method.

- Deprecates function ``xoutil.iterators.fake_dict_iteritems``.

- Deprecates `xoutil.objects.metaclass`:class: in favor for
  `xoutil.eight.meta.metaclass`:func:.
