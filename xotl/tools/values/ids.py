#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

r"""Utilities to obtain identifiers that are unique at different contexts.

Contexts could be global, host local or application local.  All standard
`uuid`:mod: tools are included in this one: `UUID`:class:, `uuid1`:func:,
`uuid3`:func:, `uuid4`:func:, `uuid5`:func:, `getnode`:func: and standard
UUIDs constants `NAMESPACE_DNS`, `NAMESPACE_URL`, `NAMESPACE_OID` and
`NAMESPACE_X500`.

This module also contains:

- `str_uuid`:func:\ : Return a string with a GUID representation, random if
  the argument is True, or a host ID if not.

.. versionadded:: 1.7.0

.. deprecated:: 2.1.0

"""

from uuid import getnode  # noqa
from uuid import (  # noqa
    NAMESPACE_DNS,
    NAMESPACE_OID,
    NAMESPACE_URL,
    NAMESPACE_X500,
    UUID,
    uuid1,
    uuid3,
    uuid4,
    uuid5,
)


def str_uuid(random=False):  # pragma: no cover
    """Return a "Global Unique ID" as a string.

    :param random: If True, a random uuid is generated (does not use host id).

    .. deprecated:: 2.1.0 Use `uuid.uuid4`:func: or `uuid.uuid1`:func:.

    """
    fn = uuid4 if random else uuid1
    return str(fn())
