#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
try:
    from ._version import get_version

    VERSION = get_version()

except ImportError:
    from ._version import get_versions

    VERSION = get_versions()["version"]


RELEASE_TAG = ""


def safe_int(x):
    try:
        return int(x)
    except ValueError:
        return x


# I won't put the release tag in the version_info tuple.  Since PEP440 is on
# the way.
VERSION_INFO = tuple(safe_int(x) for x in VERSION.split("."))


del safe_int
