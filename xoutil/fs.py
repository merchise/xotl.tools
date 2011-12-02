# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.fs
#----------------------------------------------------------------------
# Copyright (c) 2011 Merchise Autrement
# All rights reserved.
#
# Author: Medardo Rodriguez
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# Created on Nov 28, 2011

'''File system utilities.'''


from __future__ import (division as _py3_division, print_function as _py3_print, 
                        unicode_literals as _py3_unicode)



def organize_repo(src, dst, pattern=None):
    '''
    Take a massive list of packages stored in the source (src), and organize in
    destination folder (dst).
    If the package name have the pattern "PRODUCT.NAME-VERSION.EXT, the product
    name is used as destination folder tail, else, first letter.
    Both path names are normalized before used.
    If 'pattern' is specified, only paths fulfilling with it are processed.
    'pattern' could be a wild-card or a regular expression.
    Not implemented at all.
    '''
    # FIXME: This is partially implemented
    import os
    from xotl import fs
    src = fs.normalize_path(src)
    dst = fs.normalize_path(dst)
    for dirpath, _dirnames, filenames in os.walk(src):
        for item in filenames:
            fname = os.path.join(dirpath, item)
            print(fname)

