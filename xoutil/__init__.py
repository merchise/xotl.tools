# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil
# ---------------------------------------------------------------------
# Copyright (c) 2013-2016 Merchise Autrement [~º/~] and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created: 2012-03-23
#

'''`xoutil` is a collection of disparate utilities that does not conform
a framework for anything. `xoutil` is essentially an extension to the
Python's standard library.

'''

from .symbols import boolean


# False value where None could be a valid value
Unset = boolean('Unset')


# False value for local scope use or where Unset could be a valid value
Undefined = boolean('Undefined')


# To be used in arguments that are currently ignored cause they are being
# deprecated. The only valid reason to use `ignored` is to signal ignored
# arguments in method's/function's signature
Ignored = boolean('Ignored')


del boolean
