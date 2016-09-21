#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.future.subprocess
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise and Contributors
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
                        absolute_import as _py3_abs_imports)


from subprocess import *    # noqa

from pprint import __all__    # noqa
__all__ = __all__ + ['call_and_check_output']


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
