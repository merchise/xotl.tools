#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Response classes used by ``urllib``.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)

from xoutil.eight import python_version


if python_version == 3:
    # Python 3 __all__ in Python 2 urllib
    from urllib.response import (    # noqa
        addbase, addclosehook, addinfo, addinfourl)
else:
    # Python 3 __all__ in Python 2 urllib
    from urllib import (    # noqa
        addbase, addclosehook, addinfo, addinfourl)

del python_version
