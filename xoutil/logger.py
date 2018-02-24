#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Standard logging helpers.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import warnings
warnings.warn('xoutil.logger is deprecated an it will be removed. '
              'Use the standard logging module.', stacklevel=2)

from xoutil.modules import _CustomModuleBase


class _LoggerModule(_CustomModuleBase):
    '''Standard logging helpers.

    Usage::

        logger.debug('Some debug message')


    Basically you may request any of the loggers attribute/method and this
    module will return the logger's attribute corresponding to the loggers of
    the calling module.  This avoids the boilerplate seen in most codes::

        logger = logging.getLogger(__name__)


    You may simply do::

        from xoutil.logger import debug
        debug('Some debug message')

    The proper logger will be selected by this module.

    '''
    @classmethod
    def _get_callers_module(cls, depth=2):
        import sys
        frame = sys._getframe(depth)
        try:
            return frame.f_globals['__name__']
        finally:
            frame = None

    def __getattr__(self, name):
        import logging
        logger = logging.getLogger(self._get_callers_module())
        attr = getattr(logger, name)
        return attr

    def __dir__(self):
        import logging
        logger = logging.getLogger(self._get_callers_module())
        return dir(logger)


import sys
sys.modules[__name__] = _LoggerModule(__name__)
del sys, _CustomModuleBase
