``xotl.tools.future.collections`` - High-performance container datatypes
========================================================================

.. module:: xotl.tools.future.collections

.. testsetup::

   from xotl.tools.future.collections import *

This module extends the standard library's `collections`:mod:.  You may use it
as a drop-in replacement in many cases.

Avoid importing ``*`` from this module since this is different in Python 2.7
and Python 3.3.  Notably importing ``abc`` is not available in Python 2.7.


.. autoclass:: defaultdict

.. autoclass:: opendict
   :members: from_enum

.. autoclass:: codedict

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

.. autoclass:: PascalSet

.. autoclass:: BitPascalSet
