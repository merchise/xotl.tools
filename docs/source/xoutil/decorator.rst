:mod:`xoutil.decorator` - Several decorators
============================================

.. module:: xoutil.decorator

This module contains several useful decorators, for several purposed. Also it
severs as a namespace for other well-defined types of decorators.

.. warning:: This modules will be progressively deprecated during the 1.6
   series.

   We feel that either `xoutil.objects`:mod: or `xoutil.functools` are a
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

.. autoclass:: memoized_property

.. autoclass:: memoized_instancemethod


Sub packages
------------

.. toctree::
   :glob:
   :maxdepth: 1

   decorator/*
