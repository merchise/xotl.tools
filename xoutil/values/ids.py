#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.ids
# ---------------------------------------------------------------------
# Copyright (c) 2015, 2016 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-08-25

'''Utilities to obtain identifiers that are unique at different contexts.

Contexts could be global, host local or application local.  All standard
`uuid`:mod: tools are included in this one: `UUID`:class:, `uuid1`:func:,
`uuid3`:func:, `uuid4`:func:, `uuid5`:func:, `getnode`:func:` and standard
UUIDs constants `NAMESPACE_DNS`, `NAMESPACE_URL`, `NAMESPACE_OID` and
`NAMESPACE_X500`.

This module also contains:

- `uuid`:func:\ : Return a string with a GUID representation, random if the
  argument is True, or a host ID if not.

- `slugify`:func:\ : Convert any object to a valid slug (mainly used with
  string parameters).

.. versionadded:: 1.7.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)


from uuid import (UUID, uuid1, uuid3, uuid4, uuid5, getnode,    # noqa
                  NAMESPACE_DNS, NAMESPACE_URL, NAMESPACE_OID, NAMESPACE_X500)


from xoutil.deprecation import inject_deprecated
import xoutil.cl.ids

__all__ = ['str_uuid', 'slugify', ]    # noqa

inject_deprecated(__all__, xoutil.cl.ids)

del xoutil.cl.ids, inject_deprecated
