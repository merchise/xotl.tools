`xotl.tools.decorator`:mod: - Several decorators
================================================

.. module:: xotl.tools.decorator

This module contains several useful decorators, for several purposed.  Also it
severs as a namespace for other well-defined types of decorators.

.. warning:: This modules will be progressively deprecated during the 1.6
   series.

   We feel that either `xotl.tools.objects`:mod: or `xotl.tools.functools` are a
   better match for some of these decorators.  But since we need to make sure
   about keeping dependencies, the deprecation won't be final until 1.7.0.
   After 1.8.0, this modules will be finally removed.

Top-level decorators
--------------------

.. autoclass:: AttributeAlias
   :members:

.. autofunction:: settle

.. autofunction:: namer

.. autofunction:: aliases

.. autofunction:: assignment_operator(func, maybe_inline=False)

.. autofunction:: instantiate(target, *args, **kwargs)

.. autofunction:: constant_bagger(func, *args, **kwds)

.. autoclass:: memoized_instancemethod




Sub packages
------------

.. toctree::
   :glob:
   :maxdepth: 1

   decorator/*
