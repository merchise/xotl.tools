#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Classes for exceptions raised by ``request``.

The base exception class in Python 3 is `URLError`:class:, but not in
Python 2.


'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)

from xoutil.eight import python_version


if python_version == 3:
    from urllib.error import ContentTooShortError    # noqa
    from urllib.error import HTTPError, URLError    # noqa
else:
    from urllib import ContentTooShortError    # noqa

    try:
        from urllib2 import HTTPError, URLError    # noqa
    except ImportError:
        pass


del python_version
