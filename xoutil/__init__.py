# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
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
# Created: Mar 23, 2012
#

'''`xoutil` is a collection of disparate utilities that does not conform
a framework for anything. `xoutil` is essentially an extension to the
Python's standard library.

xoutil provides a basic implementation of :mod:`execution contexts
<xoutil.context>`, that allows a programmer to enter/exit an execution
context; which then may signal a component to behave differently. This
implementation of contexts does not support distribution, though. But it's
useful to implement components that have two different interfaces according to
the context in which they are invoked. In this regard, contexts are a thin
(but very idiomatic) alternative to some of the design patterns found
elsewhere.

'''


from ._values import Unset, Undefined, Ignored
