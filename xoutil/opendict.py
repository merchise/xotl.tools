#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.opendict
#----------------------------------------------------------------------
# Copyright (c) 2011 Merchise Autrement
# All rights reserved.
#
# Author: Manuel Vázquez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Dec 13, 2011

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)


from xoutil import collections
from xoutil.deprecation import inject_deprecated

__docstring_format__ = 'rst'
__author__ = 'manu'


__all__ = (b'opendict',)
inject_deprecated(__all__, collections)
