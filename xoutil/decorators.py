#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.decorators
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 7 janv. 2013


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from xoutil.string import names
from xoutil import decorator
from xoutil.deprecation import inject_deprecated

__all__ = names('AttributeAlias',
                'settle',
                'namer',
                'aliases',
                'instantiate',
                'assignment_operator',)

inject_deprecated(__all__, decorator)
