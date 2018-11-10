#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
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
        if modname:
            result = sys.modules[full_name] = importlib.import_module(modname)
            return result
        else:
            raise ImportError(modname)


sys.meta_path.append(Hook())
