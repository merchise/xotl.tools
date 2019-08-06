`xotl.tools.objects`:mod: - Functions for dealing with objects
==============================================================

.. automodule:: xotl.tools.objects
   :members: validate_attrs, iterate_over, smart_getter,
	     smart_getter_and_deleter, popattr, setdefaultattr, copy_class,
	     fulldir, classproperty, import_object

.. autofunction:: get_first_of(sources, *keys, default=None, pred=None)

.. autofunction:: xdir(obj, filter=None, attr_filter=None, value_filter=None, getattr=None)

.. autofunction:: fdir(obj, filter=None, attr_filter=None, value_filter=None, getattr=None)

.. autofunction:: smart_copy(*sources, target, *, defaults=False)

.. autofunction:: extract_attrs(obj, *names, default=Unset)

.. autofunction:: traverse(obj, path, default=Unset, sep='.', getter=None)

.. autofunction:: get_traverser(*paths, default=Unset, sep='.', getter=None)

.. autofunction:: dict_merge(*dicts, **other)

.. autofunction:: pop_first_of(source, *keys, default=None)

.. autofunction:: fix_method_documentation

.. autofunction:: multi_getter

.. autofunction:: get_branch_subclasses

.. autofunction:: iter_final_subclasses

.. autofunction:: get_final_subclasses

.. autofunction:: FinalSubclassEnumeration

.. autofunction:: save_attributes(obj, *attributes, getter=None, setter=None)

.. autofunction:: temp_attributes(obj, attrs, getter=None, setter=None)

.. autoclass:: memoized_property
   :members: reset

   .. versionadded:: 1.8.1 Ported from ``xoutil.decorator.memoized_property``.

.. autofunction:: delegator

.. autoclass:: DelegatedAttribute
