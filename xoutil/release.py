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

VERSION = '1.8.3'


def dev_tag_installed():
    import pkg_resources
    try:
        dist = pkg_resources.get_distribution('xoutil')
        full_version = dist.version
        # FIX: Below line is not working anymore
        base = dist.parsed_version.base_version
        return full_version[len(base):]
    except:
        return None


RELEASE_TAG = dev_tag_installed() or ''


def safe_int(x):
    try:
        return int(x)
    except ValueError:
        return x


# I won't put the release tag in the version_info tuple.  Since PEP440 is on
# the way.
VERSION_INFO = tuple(safe_int(x) for x in VERSION.split('.'))


del safe_int
