- Fix a bug in `xoutil.objects.extract_attrs`:func:.  It was not raising
  exceptions when some attribute was not found and `default` was not provided.

  Also now the function supports paths like
  `xoutil.objects.get_traverser`:func:.
