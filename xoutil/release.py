#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

VERSION = '1.9.6'


def dev_tag_installed():
    import pkg_resources
    try:
        dist = pkg_resources.get_distribution('xoutil')
        full_version = dist.version
        # FIX: Below line is not working anymore
        base = dist.parsed_version.base_version
        return full_version[len(base):]
    except Exception:
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
