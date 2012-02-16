#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.fs.path
#----------------------------------------------------------------------
# Copyright (c) 2012 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on Feb 16, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

import os


__docstring_format__ = 'rst'
__author__ = 'manu'



def normalize_path(path):
    '''
    Normalize path:
      * expanding '~' and '~user' constructions.
      * eliminating double slashes
      * converting to absolute.
    '''
    res = os.path.abspath(os.path.expanduser(path))
    # TODO: Analyze if the resulting name must be encoded.
#    import sys
#    encoding = sys.getfilesystemencoding()
#    if encoding:
#        res = res.encode(encoding)
    return res


def get_module_path(module_or_name):
    # TODO: [med] Standardize this
    mod = __import__(module_or_name) if isinstance(module_or_name, basestring) else module_or_name
    path = mod.__path__[0] if hasattr(mod, '__path__') else mod.__file__
    return os.path.abspath(os.path.dirname(path).decode('utf-8'))



def shorten_module_filename(filename):
    '''
    A filename, normally a module o package name, is shortened looking
    his head in all python path.
    '''
    import sys, os.path
    path = sys.path[:]
    path.sort(lambda x, y: len(y) - len(x))
    for item in path:
        if item and filename.startswith(item):
            filename = filename[len(item):]
            if filename.startswith(os.path.sep):
                filename = filename[len(os.path.sep):]
    for item in ('__init__.py', '__init__.pyc'):
        if filename.endswith(item):
            filename = filename[:-len(item)]
            if filename.endswith(os.path.sep):
                filename = filename[:-len(os.path.sep)]
    return shorten_user(filename)



def shorten_user(filename):
    '''
    A filename is shortened looking for the $HOMe in his head and replacing
    it by '~'.
    '''
    import os.path
    home = os.path.expanduser('~')
    if filename.startswith(home):
        filename = os.path.join('~', filename[len(home):])
    return filename



__all__ = ('normalize_path', 'get_module_path', 'shorten_module_filename',
           'shorten_user',)
