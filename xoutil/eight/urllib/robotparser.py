#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Parsing ``robots.txt`` files.

Uses module Copyright (C) 2000  Bastian Kleineidam.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)


from xoutil.eight import python_version


if python_version == 3:
    # __all__
    try:
        from urllib.robotparser import RobotFileParser    # noqa
    except ImportError:
        pass

    # Not in __all__
    try:
        from urllib.robotparser import RuleLine, Entry    # noqa
    except ImportError:
        pass

else:
    # __all__
    try:
        from robotparser import RobotFileParser    # noqa
    except ImportError:
        pass

    # Not in __all__
    try:
        from robotparser import RuleLine, Entry    # noqa
    except ImportError:
        pass

    # Not in Python 3?
    try:
        from robotparser import URLopener    # noqa
    except ImportError:
        pass


del python_version
