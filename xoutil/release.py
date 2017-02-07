#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.release
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~] and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2012-04-01


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

# FIXME: Use literal functions
from xoutil.versions import dev_tag_installed, parse_version_info

VERSION = '1.8.0'

RELEASE_TAG = dev_tag_installed('xoutil') or ''

VERSION_INFO = parse_version_info(VERSION)

del dev_tag_installed, parse_version_info
