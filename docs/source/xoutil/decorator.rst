:mod:`xoutil.decorator` - Several decorators
============================================

.. module:: xoutil.decorator

This module contains several useful decorators, for several purposed. Also it
severs as a namespace for other well-defined types of decorators.

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
