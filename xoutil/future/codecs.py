# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.future.codecs
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the Python Software Licence as of Python 3.3.
#
# Created on 2017-09-30

'''Codec registry, base classes and tools.

In this module, some additions for `codecs` standard module.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from codecs import *    # noqa
import codecs as _stdlib
from codecs import __all__    # noqa
__all__ = list(__all__)

from xoutil.future import _past    # noqa
_past.dissuade()
del _past
