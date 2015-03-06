:mod:`xoutil.objects` - Functions for dealing with objects
==========================================================

.. automodule:: xoutil.objects
   :members: validate_attrs, iterate_over, smart_getter,
	     smart_getter_and_deleter, popattr, setdefaultattr, copy_class,
	     metaclass, attrclass, fulldir, classproperty

.. autofunction:: get_first_of(sources, *keys, default=None, pred=None)

.. autofunction:: xdir(obj, filter=None, attr_filter=None, value_filter=None, getattr=None)

.. autofunction:: fdir(obj, filter=None, attr_filter=None, value_filter=None, getattr=None)

.. autofunction:: smart_copy(*sources, target, *, defaults=False)

.. autofunction:: extract_attrs(obj, *names, default=Unset)

.. autofunction:: traverse(obj, path, default=Unset, sep='.', getter=None)

.. autofunction:: get_traverser(*paths, default=Unset, sep='.', getter=None)

.. autofunction:: dict_merge(*dicts, **other)

.. autofunction:: smart_getattr(name, *sources, **kwargs)

.. autofunction:: pop_first_of(source, *keys, default=None)

.. function:: get_and_del_attr(obj, name, default=None)

   Deprecated alias for :func:`popattr`.

.. function:: get_and_del_first_of(source, *keys, default=None)

   Deprecated alias for :func:`pop_first_of`.
