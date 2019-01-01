``xotl.tools.future.collections`` - High-performance container datatypes
========================================================================

.. module:: xotl.tools.future.collections

This module extends the standard library's `collections`:mod:.  You may use it
as a drop-in replacement in many cases.

Avoid importing ``*`` from this module since this is different in Python 2.7
and Python 3.3.  Notably importing ``abc`` is not available in Python 2.7.

We have backported several Python 3.3 features but not all.


.. autoclass:: defaultdict

.. autoclass:: opendict
   :members: from_enum

.. autoclass:: codedict

.. autoclass:: Counter

   .. note:: Backported from Python 3.3. In Python 3.3 this is an alias.

.. autoclass:: OrderedDict

   .. note:: Backported from Python 3.3. In Python 3.3 this is an alias.

.. autoclass:: OpenDictMixin

.. autoclass:: OrderedSmartDict

.. autoclass:: SmartDictMixin

.. autoclass:: StackedDict
   :members: push_level, pop_level, level, peek

   .. method:: pop()

      A deprecated alias for `pop_level`:meth:.

      .. deprecated:: 1.7.0

   .. method:: push(*args, **kwargs)

      A deprecated alias for `push_level`:meth:.

      .. deprecated:: 1.7.0


.. class:: ChainMap(*maps)

   A ChainMap groups multiple dicts or other mappings together to create a
   single, updateable view.  If no maps are specified, a single empty
   dictionary is provided so that a new chain always has at least one mapping.

   The underlying mappings are stored in a list.  That list is public and can
   accessed or updated using the maps attribute.  There is no other state.

   Lookups search the underlying mappings successively until a key is found.
   In contrast, writes, updates, and deletions only operate on the first
   mapping.

   A ChainMap incorporates the underlying mappings by reference.  So, if one of
   the underlying mappings gets updated, those changes will be reflected in
   ChainMap.

   All of the usual dictionary methods are supported.  In addition, there is a
   maps attribute, a method for creating new subcontexts, and a property for
   accessing all but the first mapping:

   .. attribute:: maps

      A user updateable list of mappings.  The list is ordered from
      first-searched to last-searched.  It is the only stored state and can be
      modified to change which mappings are searched.  The list should always
      contain at least one mapping.

   .. method:: new_child(m=None)

      Returns a new `ChainMap`:class: containing a new map followed by all of
      the maps in the current instance.  If ``m`` is specified, it becomes the
      new map at the front of the list of mappings; if not specified, an empty
      dict is used, so that a call to ``d.new_child()`` is equivalent to:
      ``ChainMap({}, *d.maps)``.  This method is used for creating subcontexts
      that can be updated without altering values in any of the parent
      mappings.

      .. versionchanged:: 1.5.5
	 The optional ``m`` parameter was added.

   .. attribute:: parents

      Property returning a new ChainMap containing all of the maps in the
      current instance except the first one.  This is useful for skipping the
      first map in the search.  Use cases are similar to those for the
      nonlocal keyword used in nested scopes.  A reference to ``d.parents`` is
      equivalent to: ``ChainMap(*d.maps[1:])``.


   .. note:: Backported from Python 3.4.  In Python 3.4 this is an alias.


.. autoclass:: PascalSet

.. autoclass:: BitPascalSet
