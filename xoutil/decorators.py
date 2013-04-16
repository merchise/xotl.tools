#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.decorators
#----------------------------------------------------------------------
# Copyright (c) 2012, 2013 Merchise Autrement and Contributors
# Copyright (c) 2009-2011 Medardo Rodríguez
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 7 janv. 2013


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from xoutil import decorator
from xoutil.deprecation import inject_deprecated

from xoutil.names import namelist

__all__ = namelist('AttributeAlias',
                   'settle',
                   'namer',
                   'aliases',
                   'instantiate',
                   'assignment_operator')

del namelist

inject_deprecated(__all__, decorator)
