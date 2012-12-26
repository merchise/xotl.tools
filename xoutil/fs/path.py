#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.fs.path
#----------------------------------------------------------------------
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodríguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Feb 16, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

import os
from os.path import (abspath, expanduser, dirname, sep, join)
from ..compat import str_base


__docstring_format__ = 'rst'
__author__ = 'manu'



def normalize_path(path):
    '''
    Normalize path by:

      - expanding '~' and '~user' constructions.
      - eliminating double slashes
      - converting to absolute.
    '''
    if not isinstance(path, str):
        import sys
        encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
        if isinstance(path, bytes):     # Python 3
            path = path.decode(encoding)
        else:
            path = path.encode(encoding)
    return abspath(expanduser(path))


def get_module_path(module):
    # TODO: [med] Standardize this
    mod = __import__(module) if isinstance(module, str_base) else module
    path = mod.__path__[0] if hasattr(mod, '__path__') else mod.__file__
    return abspath(dirname(path).decode('utf-8'))



def shorten_module_filename(filename):
    '''
    A filename, normally a module o package name, is shortened looking
    his head in all python path.
    '''
    import sys
    path = sys.path[:]
    path.sort(lambda x, y: len(y) - len(x))
    for item in path:
        if item and filename.startswith(item):
            filename = filename[len(item):]
            if filename.startswith(sep):
                filename = filename[len(sep):]
    for item in ('__init__.py', '__init__.pyc'):
        if filename.endswith(item):
            filename = filename[:-len(item)]
            if filename.endswith(sep):
                filename = filename[:-len(sep)]
    return shorten_user(filename)



def shorten_user(filename):
    '''
    A filename is shortened looking for the (expantion) $HOME in his head and
    replacing it by '~'.

    '''
    home = expanduser('~')
    if filename.startswith(home):
        filename = join('~', filename[len(home):])
    return filename



__all__ = ('normalize_path', 'get_module_path', 'shorten_module_filename',
           'shorten_user',)
