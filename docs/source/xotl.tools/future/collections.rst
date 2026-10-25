``xotl.tools.future.collections`` - High-performance container datatypes
========================================================================

.. module:: xotl.tools.future.collections

This module extends the standard library's `collections`:mod:.

.. testsetup::

   from xotl.tools.future.collections import *

.. autoclass:: DefaultDict

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
