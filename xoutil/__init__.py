#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Transition to a new namespace
-----------------------------

Since version 2.1, we're transitioning to another name: ``xotl.tools``.  This
is to align ``xoutil`` as a fundamental part of our family of projects under
the ``xotl`` namespace.  *Xotl* is a Nahuatl word which may stand for
'foundation'.  ``xoutil`` is part of the foundation of many of our projects.

Backwards compatible imports
----------------------------

Since 2.1, every module importable from ``xoutil`` is actually under the
namespace ``xotl.tools``; so importing, for instance, from
``xoutil.future.datetime`` should be updated to
`xotl.tools.future.datetime`:mod:.

Importing from ``xoutil`` will still be possible in all versions before 3.0.
You won't have to change all your imports right away.


Distribution of ``xoutil``
--------------------------

Will continue to distribute both `xotl.tools <xotl-tools-dist_>`__ and `xoutil
<xoutil-dist_>`__ (with the same codebase) for the entire 2.1.x series.  From
version 2.2.0+ will distruibute only ``xotl.tools``, but keep the backwards
import up to 3.0.

.. warning:: Don't depend on both ``xoutil`` and ``xotl.tools``.  We use the
   same codebase for both distributions; which means you'll get the same code,
   but if you install different versions you may get a crippled system.

.. _xotl-tools-dist: https://pypi.org/project/xotl.tools
.. _xoutil-dist: https://pypi.org/project/xoutil

"""

import importlib
import sys
from importlib.abc import MetaPathFinder

XOUTIL_NAMESPACE = "xoutil."
XOTL_TOOLS_NS = "xotl.tools."


class Hook(MetaPathFinder):
    def find_module(self, full_name, path=None):
        name = self._from_xoutil_to_xotl(full_name)
        if name:
            return self

    def _from_xoutil_to_xotl(self, full_name):
        if full_name.startswith(XOUTIL_NAMESPACE):
            path = full_name[len(XOUTIL_NAMESPACE) :]
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
            import warnings

            warnings.warn(
                ("Importing from xoutil ({}) is deprecated; " "import from xotl.tools ({})").format(
                    full_name, modname
                )
            )
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
