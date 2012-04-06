# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.fs
#----------------------------------------------------------------------
# Copyright (c) 2011 Merchise Autrement
# All rights reserved.
#
# Author: Medardo Rodriguez
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
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
# Created on Nov 28, 2011

'''File system utilities.'''


from __future__ import (division as _py3_division, print_function as _py3_print,
                        unicode_literals as _py3_unicode)


import os
from re import compile as _re_compile
from .path import normalize_path, get_module_path, shorten_module_filename, shorten_user


re_magic = _re_compile('[*?[]')
has_magic = lambda s: re_magic.search(s) is not None


def _get_regex(pattern=None, regex_pattern=None, shell_pattern=None):
    from functools import reduce
    import fnmatch
    arg_count = reduce(lambda count, p: count + (1 if p is not None else 0), (pattern, regex_pattern, shell_pattern), 0)
    if arg_count == 1:
        if pattern is not None:
            if pattern.startswith('(?'):
                regex_pattern = pattern
            else:
                shell_pattern = pattern
        return _re_compile(regex_pattern or fnmatch.translate(shell_pattern))
    elif arg_count == 0:
        return None
    else:
        raise TypeError('"_get_regex()" takes at most 1 argument (%s given)' % arg_count)



def iter_files(top='.', pattern=None, regex_pattern=None, shell_pattern=None):
    '''Iterate filenames recursively.'''
    regex = _get_regex(pattern, regex_pattern, shell_pattern)
    for dirpath, _dirs, filenames in os.walk(normalize_path(top)):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            if (regex is None) or regex.search(path):
                yield path



def iter_dirs(top='.', pattern=None, regex_pattern=None, shell_pattern=None):
    '''Itererate directories recursively'''
    regex = _get_regex(pattern, regex_pattern, shell_pattern)
    for path, _dirs, _files in os.walk(normalize_path(top)):
        if (regex is None) or regex.search(path):
            yield path



def regex_rename(top, pattern, repl):
    '''
    Rename files recursively using regular expressions substitution.
      - top: the root directory to start walking.
      - pattern: regular expression pattern; for example "(?i)\.jpg$"
      - repl: string to use a replacement (for example ".jpeg")
    '''
    from re import subn as _re_subn
    if isinstance(pattern, basestring):
        pattern = _re_compile(pattern)
    for path, _dirs, files in os.walk(top):
        for item in files:
            new_file, count = _re_subn(pattern, repl, item)
            if count > 0:
                old = os.path.join(path, item)
                new = os.path.join(path, new_file)
                os.rename(old, new)



def rename_wrong(top='.', current_encoding=None, target_encoding=None,
                 verbose=False):
    'Converts filenames from one encoding to another if the current is wrong.'
    import sys
    wrongs = []
    if current_encoding is None:
        current_encoding = sys.getfilesystemencoding() or 'utf-8'
    for fn in os.listdir(top):
        encoding = sys.getfilesystemencoding() or 'utf-8'
        try:
            test = fn.decode(encoding) if not isinstance(fn, unicode) else fn
            if verbose:
                print('>>> No problem with:', test)
        except:
            wrongs.append(fn)
        if wrongs:
            if target_encoding is None:
                try:
                    import chardet
                except:
                    chardet = None
            else:
                te = target_encoding
        try:
            if verbose:
                print('>>> PROBLEM with:', fn)
            if target_encoding is None:
                dir = os.path.dirname(fn)
                
            else:
                te = target_encoding
                
            new = fn.decode()    # Use "chardet.detect" or 'ibm857'
            os.rename(fn, new)
            print('*'*8, new)
        except Exception as error:
            pass



filter_not_hidden = lambda path, stat_info: (path[0] != '.') and ('/.' not in path)

filter_false = lambda path, stat_info: False

def get_regex_filter(regex):
    '''Return a filter for "walk" based on a regular expression.'''
    if isinstance(regex, basestring):
        regex = _re_compile(regex)
    def _filter(path, stat_info):
        return regex.match(os.path.basename(path)) is not None
    return _filter


def get_wildcard_filter(pattern):
    '''Return a filter for "walk" based on a wildcard pattern a la fnmatch.'''
    regex = _get_regex(pattern)
    def _filter(path, stat_info):
        return regex.match(os.path.basename(path)) is not None
    return _filter


def get_mime_filter(mime_start):
    import mimetypes
    def _filter(path, stat_info):
        t = mimetypes.guess_type(path)[0]
        return t.startswith(mime_start) if t else False
    return _filter


def nice_size(size):
    tails = ' KMGT'
    i, high = 0, len(tails) - 1
    while (size >= 1024) and (i < high):
        size /= 1024
        i += 1
    res = ('%.2f' % size).rstrip('0').rstrip('.')
    return '%s%s' % (res, tails[i])


def stat(path):
    '''Return file or file system status.'''
    try:
        return os.stat(path)
    except os.error:
        return None


def lstat(path):
    '''Like stat(path), but do not follow symbolic links.'''
    try:
        return os.lstat(path)
    except os.error:
        return None


def set_stat(fname, stat_info):
    os.chmod(fname, stat_info.st_mode)
    os.chown(fname, stat_info.st_uid, stat_info.st_gid)
    os.utime(fname, (stat_info.st_atime, stat_info.st_mtime))


def listdir(path):
    try:
        return os.listdir(normalize_path(path))
    except os.error:
        return []


def _list_magic(dirname, pattern):
    re = _get_regex(pattern)
    for name in listdir(dirname or os.curdir):
        if re.match(name):
            full = os.path.join(dirname, name)
            yield full, lstat(full)


def _list_one(fname):
    st = lstat(fname)
    if st:
        yield fname, st


def _list(pattern):
    from stat import S_ISDIR as _ISDIR
    if has_magic(pattern):
        head, tail = os.path.split(pattern)
        for dirname, st in _list(head):
            if _ISDIR(st.st_mode):
                if has_magic(tail):
                    items = _list_magic(dirname, tail)
                elif tail:
                    items = _list_one(os.path.join(dirname, tail))
                else:
                    items = ((dirname, st),)
            for item in items:
                yield item
    else:
        for item in _list_one(pattern) if pattern else (('', lstat(os.curdir)),):
            yield item



def imap(func, pattern):
    '''
    yield func(file_0, stat_0), func(file_1, stat_1), ...

    for each dir path, "pattern" may contain:
      * Simple shell-style wildcards a la fnmatch.
      * Regex if pattern starts with '(?'.
        Expressions must be valid, as in "(?:[^.].*)$" or "(?i).*\.jpe?g$".
        Remember add end '$' if needed.
    '''
    for item, st in _list(pattern):
        res = func(item, st)
        if res is not None:
            yield res


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
    src = normalize_path(src)
    dst = normalize_path(dst)
    for dirpath, _dirnames, filenames in os.walk(src):
        for item in filenames:
            fname = os.path.join(dirpath, item)
            print(fname)

