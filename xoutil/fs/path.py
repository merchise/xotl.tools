#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Extensions to os.path

Functions inside this module must not have side-effects on the
file-system. This module re-exports (without change) several functions from the
`os.path`:mod: standard module.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import sys
from os.path import (abspath, expanduser, dirname, sep, normpath,
                     join as _orig_join)

from xoutil.future.functools import power as pow_

__all__ = ('abspath', 'expanduser', 'dirname', 'sep', 'normpath', 'rtrim',
           'fix_encoding', 'join', 'normalize_path',
           'shorten_module_filename', 'shorten_user')


# TODO: import all in "from os.path import *"

def rtrim(path, n=1):
    """Trims the last `n` components of the pathname `path`.

    This basically applies `n` times the function `os.path.dirname` to `path`.

    `path` is normalized before proceeding (but not tested to exists).

    .. versionchanged:: 1.5.5 `n` defaults to 1.  In this case rtrim is
                        identical to `os.path.dirname`:func:.

    Example::

      >>> rtrim('/tmp/a/b/c/d', 3)
      '/tmp/a'

      # It does not matter if `/` is at the end
      >>> rtrim('/tmp/a/b/c/d/', 3)
      '/tmp/a'

    """
    return pow_(dirname, n)(normalize_path(path))


def fix_encoding(name, encoding=None):
    '''Fix encoding of a file system resource name.

    `encoding` is ignored if `name` is already a `str`.

    '''
    if not isinstance(name, str):
        if not encoding:
            from xoutil.future.codecs import force_encoding
            encoding = force_encoding(sys.getfilesystemencoding())
        fixer = name.decode if isinstance(name, bytes) else name.encode
        return fixer(encoding)
    else:
        return name


def join(base, *extras):
    '''Join two or more pathname components, inserting '/' as needed.

    If any component is an absolute path, all previous path components
    will be discarded.

    Normalize path (after join parts), eliminating double slashes, etc.

    '''
    try:
        path = _orig_join(base, *extras)
    except Exception:  # TODO: @med which exceptions expected?
        base = fix_encoding(base)
        extras = [fix_encoding(extra) for extra in extras]
        path = _orig_join(base, *extras)
    return normpath(path)


def normalize_path(base, *extras):
    '''Normalize path by:

    - expanding '~' and '~user' constructions.
    - eliminating double slashes
    - converting to absolute.

    '''
    # FIXME: [med] Redundant "path" in name "xoutil.fs.path.normalize_path"
    try:
        path = _orig_join(base, *extras)
    except Exception:  # TODO: @med which exceptions expected?
        path = join(base, *extras)
    return abspath(expanduser(path))


def shorten_module_filename(filename):
    '''A filename, normally a module o package name, is shortened looking his
    head in all python path.

    '''
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
    '''A filename is shortened looking for the (expantion) $HOME in his head
    and replacing it by '~'.

    '''
    home = expanduser('~')
    if filename.startswith(home):
        filename = _orig_join('~', filename[len(home):])
    return filename
