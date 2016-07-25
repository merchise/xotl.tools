#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.versions
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-07-25

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)


def dev_tag_installed(dist_name):
    import pkg_resources
    try:
        dist = pkg_resources.get_distribution(dist_name)
        full_version = dist.version
        # FIX: Below line is not working anymore
        base = dist.parsed_version.base_version
        return full_version[len(base):]
    except:
        return None


def parse_version_info(VERSION):
    # I won't put the release tag in the version_info tuple.  Since PEP440 is
    # on the way.

    def safe_int(x):
        try:
            return int(x)
        except ValueError:
            return x

    return tuple(safe_int(x) for x in VERSION.split('.'))
