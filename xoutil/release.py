#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.release
# ---------------------------------------------------------------------
# Copyright (c) 2013-2015 Merchise Autrement and Contributors
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
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

VERSION = '1.6.9'


def dev_tag_installed():
    import pkg_resources
    try:
        dist = pkg_resources.get_distribution('xoutil')
        full_version = dist.version
        base = dist.parsed_version.base_version
        return full_version[len(base):]
    except:
        return None

RELEASE_TAG = dev_tag_installed() or ''
