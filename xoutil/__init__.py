#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
'''Backwards incompatible imports.

Since ``xoutil 2.1``, we're transitioning to another name: ``xotl.tools``.
This makes ``xoutil`` part of our family of projects under the ``xotl``
namespace.

'''

import sys
import importlib
from importlib.abc import MetaPathFinder

XOUTIL_NAMESPACE = 'xoutil.'
XOTL_TOOLS_NS = 'xotl.tools.'


class Hook(MetaPathFinder):
    def find_module(self, full_name, path=None):
        name = self._from_xoutil_to_xotl(full_name)
        if name:
            return self

    def _from_xoutil_to_xotl(self, full_name):
        if full_name.startswith(XOUTIL_NAMESPACE):
            path = full_name[len(XOUTIL_NAMESPACE):]
            return XOTL_TOOLS_NS + path
        else:
            return None

    def load_module(self, full_name):
        result = sys.modules.get(full_name, None)
        if result:
            return result
        modname = self._from_xoutil_to_xotl(full_name)
        result = None
        if modname:
            result = sys.modules.get(modname, None)
        if not result and modname:
            result = importlib.import_module(modname)
        if result:
            sys.modules[modname] = sys.modules[full_name] = result
            return result
        else:
            raise ImportError(modname)


# I have to put this meta path before Python's standard, because otherwise
# importing like this:
#
#     from xoutil.future.datetime import TimeSpan
#
# First imports 'xoutil.future' with our Hook, but afterwards,
# 'xoutil.future.datetime' is found by _frozen_importlib_external.PathFinder
# instead of our own Hook which maintains 100% backwards compatibility of
# imports.
sys.meta_path.insert(0, Hook())
