:mod:`xoutil.objects` - Functions for dealing with objects
==========================================================

.. automodule:: xoutil.objects
   :members: validate_attrs, get_first_of, smart_getter,
	     smart_getter_and_deleter, smart_getattr, get_and_del_attr,
	     get_and_del_key, setdefaultattr, copy_class, metaclass, attrclass,
	     fulldir, classproperty

.. autofunction:: xdir(obj, filter=None, attr_filter=None, value_filter=None, getattr=None)

.. autofunction:: fdir(obj, filter=None, attr_filter=None, value_filter=None, getattr=None)

.. autofunction:: smart_copy(*sources, target, defaults=False)

.. autofunction:: extract_attrs(obj, *attrs, default=Unset)

.. autofunction:: traverse(obj, path, default=Unset, sep='.', getter=None)

.. autofunction:: dict_merge(*dicts, **other)
