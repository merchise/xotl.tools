``xotl.tools.future.collections`` - High-performance container datatypes
========================================================================

.. module:: xotl.tools.future.collections

This module extends the standard library's `collections`:mod:.

.. testsetup::

   from xotl.tools.future.collections import *

.. autoclass:: DefaultDict

.. class:: defaultdict

   This a deprecated alias of `DefaultDict`:class: because it clashes with the
   standard one hurting type-hints.

   .. deprecated:: 3.0.0


.. autoclass:: opendict
   :members: from_enum

.. autoclass:: codedict

.. autoclass:: OpenDictMixin

.. autoclass:: OrderedSmartDict

.. autoclass:: SmartDictMixin

.. autoclass:: StackedDict
   :members: push_level, pop_level, level, peek

.. autoclass:: PascalSet

.. autoclass:: BitPascalSet
