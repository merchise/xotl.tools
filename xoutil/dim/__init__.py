#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Facilities to work with `concrete numbers`_.

The name `dim`:mod: is a short of dimension.  We borrow it from the topic
"dimensional analysis", even though the scope of this module is less
ambitious.

This module is divided in two major parts:

- `xoutil.dim.meta`:mod: which allows to define almost any kind of quantity
  decorated with a unit.

- Other modules ``xoutil.dim.*`` which contains applications of the
  definitions in `~xoutil.dim.meta`:mod:.  In particular,
  `xoutil.dim.base`:mod: contains the `base quantities`_ for the
  `International System of Quantities`_.


.. _concrete numbers: https://en.wikipedia.org/wiki/Concrete_number

.. _base quantities: https://en.wikipedia.org/wiki/Base_quantity

.. _International System of Quantities: \
   https://en.wikipedia.org/wiki/International_System_of_Quantities

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)
