#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.subprocess
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-01-11

'''Extensions the `subprocess` module in the standard library.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

import subprocess as _pm
from xoutil.modules import copy_members as _copy_members
_copy_members(_pm)

Popen = _pm.Popen
PIPE = _pm.PIPE

from xoutil.names import strlist as strs
__all__ = strs('call_and_check_output')
__all__.extend(getattr(_pm, '__all__', dir(_pm)))
del strs, _pm, _copy_members


def call_and_check_output(*popenargs, **kwargs):
    '''Combines `call` and `check_output`. Returns a tuple ``(returncode,
    output, err_output)``.

    '''
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = Popen(stdout=PIPE, *popenargs, **kwargs)
    output, err = process.communicate()
    retcode = process.poll()
    return (retcode, output, err)
