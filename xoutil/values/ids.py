#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Utilities to obtain identifiers that are unique at different contexts.

Contexts could be global, host local or application local.  All standard
`uuid`:mod: tools are included in this one: `UUID`:class:, `uuid1`:func:,
`uuid3`:func:, `uuid4`:func:, `uuid5`:func:, `getnode`:func: and standard
UUIDs constants `NAMESPACE_DNS`, `NAMESPACE_URL`, `NAMESPACE_OID` and
`NAMESPACE_X500`.

This module also contains:

- `str_uuid`:func:\ : Return a string with a GUID representation, random if
  the argument is True, or a host ID if not.

.. versionadded:: 1.7.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)

from uuid import (UUID, uuid1, uuid3, uuid4, uuid5, getnode,    # noqa
                  NAMESPACE_DNS, NAMESPACE_URL, NAMESPACE_OID, NAMESPACE_X500)


def str_uuid(random=False):
    '''Return a "Global Unique ID" as a string.

    :param random: If True, a random uuid is generated (does not use host id).

    '''
    fn = uuid4 if random else uuid1
    return str(fn())
