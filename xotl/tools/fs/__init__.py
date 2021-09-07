#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""File system utilities.

This module contains file-system utilities that could have side-effects. For
path-handling functions that have no side-effects look at
`xotl.tools.fs.path`:mod:.

"""


import os
import sys
from re import compile as _rcompile

from xotl.tools.fs.path import normalize_path

re_magic = _rcompile("[*?[]")
has_magic = lambda s: re_magic.search(s) is not None


def _get_regex(pattern=None, regex_pattern=None, shell_pattern=None):
    import fnmatch
    from functools import reduce

    from xotl.tools.params import check_count

    arg_count = reduce(
        lambda count, p: count + (1 if p is not None else 0),
        (pattern, regex_pattern, shell_pattern),
        0,
    )
    check_count(arg_count, 0, 1, caller="_get_regex")  # XXX: WTF?!
    if arg_count == 1:
        if pattern is not None:
            if pattern.startswith("(?") or pattern.startswith("^(?"):
                regex_pattern = pattern
            else:
                shell_pattern = pattern
        return _rcompile(regex_pattern or fnmatch.translate(shell_pattern))
    elif arg_count == 0:
        return None


def iter_files(
    top=".",
    pattern=None,
    regex_pattern=None,
    shell_pattern=None,
    followlinks=False,
    maxdepth=None,
):
    """Iterate filenames recursively.

    :param top: The top directory for recurse into.
    :param pattern: A pattern of the files you want to get from the iterator.
                    It should be a string. If it starts with "(?" it will be
                    regarded as a regular expression, otherwise a shell
                    pattern.

    :param regex_pattern: An *alternative* to `pattern`. This will always be
                          regarded as a regular expression.

    :param shell_pattern: An *alternative* to `pattern`. This should be a
                          shell pattern.

    :param followlinks: The same meaning that in `os.walk`.

    :param maxdepth: Only files above this level will be yielded. If None, no
                     limit is placed.

    .. warning:: It's an error to pass more than pattern argument.

    .. versionchanged:: 1.2.1 Added parameters `followlinks` and `maxdepth`.

    """
    regex = _get_regex(pattern, regex_pattern, shell_pattern)
    depth = 0
    for dirpath, _dirs, filenames in os.walk(
        normalize_path(top), topdown=True, followlinks=followlinks
    ):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            if (regex is None) or regex.search(path):
                yield path
        if maxdepth is not None:
            depth += 1
            if depth >= maxdepth:
                _dirs[:] = []


# ------------------------------ iter_dict_files ------------------------------
_REGEX_PYTHON_PACKAGE = _rcompile(
    r"^(?P<dir>.+(?=/)/)?"
    r"(?P<packagename>[^/_-]+?)"
    r"([-_][Vv]?(?P<version>\d+([.-_]\w+)*))?"
    r"(?P<ext>[.](tar[.](gz|bz2)|zip|egg|tgz))$"
)

_REGEX_DEFAULT_ALLFILES = _rcompile(
    r"^(?P<dir>.+(?=/)/)?" r"(?P<filename>[^/]+?)" r"([.](?P<ext>[^.]+))?$"
)


def iter_dict_files(top=".", regex=None, wrong=None, followlinks=False):
    """
    Iterate filenames recursively.

    :param top: The top directory for recurse into.

    :param regex: Regular expression with group definitions to match.

    :param wrong: A key to store full name of not matching files.

    :param followlinks: The same meaning that in `os.walk`.

    .. versionadded:: 1.2.0

    .. versionchanged:: 1.2.1 Added parameter `followlinks`.

    """
    if regex:
        if isinstance(regex, str):
            regex = _rcompile(regex)
    else:
        regex = _REGEX_DEFAULT_ALLFILES
    for dirpath, _dirs, filenames in os.walk(normalize_path(top), followlinks=followlinks):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            match = regex.match(path)
            if match:
                yield match.groupdict()
            elif wrong is not None:
                yield {wrong: path}


def iter_dirs(top=".", pattern=None, regex_pattern=None, shell_pattern=None):
    """
    Iterate directories recursively.

    The params have analagous meaning that in `iter_files`:func: and the same
    restrictions.

    """
    regex = _get_regex(pattern, regex_pattern, shell_pattern)
    for path, _dirs, _files in os.walk(normalize_path(top)):
        if (regex is None) or regex.search(path):
            yield path


def rmdirs(
    top=".",
    pattern=None,
    regex_pattern=None,
    shell_pattern=None,
    exclude=None,
    confirm=None,
):
    """Removes all empty dirs at `top`.

    :param top: The top directory to recurse into.

    :param pattern: A pattern of the dirs you want to remove.
                    It should be a string. If it starts with "(?" it will be
                    regarded as a regular expression, otherwise a shell
                    pattern.

    :param exclude: A pattern of the dirs you DON'T want to remove.  It should
                    be a string. If it starts with "(?" it will be regarded as
                    a regular expression, otherwise a shell pattern. This is a
                    simple commodity to have you not to negate complex
                    patterns.

    :param regex_pattern: An *alternative* to `pattern`. This will always be
                          regarded as a regular expression.

    :param shell_pattern: An *alternative* to `pattern`. This should be a
                          shell pattern.

    :param confirm: A callable that accepts a single argument, which is
                    the path of the directory to be deleted. `confirm`
                    should return True to allow the directory to be
                    deleted. If `confirm` is None, then all matched dirs
                    are deleted.

    .. note:: In order to avoid common mistakes we won't attempt to
              remove mount points.

    .. versionadded:: 1.1.3

    """
    regex = _get_regex(pattern, regex_pattern, shell_pattern)
    exclude = _get_regex(exclude)
    if confirm is None:
        confirm = lambda _: True
    for path, _dirs, _files in os.walk(normalize_path(top)):
        # XXX: Make clearest next condition
        if (
            (regex is None or regex.search(path))
            and (exclude is None or not exclude.search(path))
            and not _dirs
            and not _files
            and confirm(path)
            and not os.path.ismount(path)
        ):
            os.rmdir(path)


def regex_rename(top, pattern, repl, maxdepth=None):
    """Rename files recursively using regular expressions substitution.

    :param top: The top directory to start walking.

    :param pattern: A regular expression pattern.  Files whose fullname
           (including the path) match the expression will be renamed.

    :param repl: String to use as replacement. You may use backreferences as
           documented in python's ``re.sub`` function.

    :param maxdepth: Only walk files up to this level.  If None, walk all
           files.

       .. versionadded:: 1.2.1

    """
    from re import subn as _re_subn

    if isinstance(pattern, str):
        pattern = _rcompile(pattern)
    depth = 0
    for path, _dirs, files in os.walk(top):
        for item in files:
            new_file, count = _re_subn(pattern, repl, item)
            if count > 0:
                old = os.path.join(path, item)
                new = os.path.join(path, new_file)
                os.rename(old, new)
        if maxdepth is not None:
            depth += 1
            if depth >= maxdepth:
                _dirs[:] = []


filter_not_hidden = lambda path, _st: (path[0] != ".") and ("/." not in path)
filter_false = lambda path, stat_info: False


def get_regex_filter(regex):
    """Return a filter for "walk" based on a regular expression."""
    if isinstance(regex, str):
        regex = _rcompile(regex)

    def _filter(path, stat_info):
        return regex.match(os.path.basename(path)) is not None

    return _filter


def get_wildcard_filter(pattern):
    """Return a filter for "walk" based on a wildcard pattern a la fnmatch."""
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
    """Formats `size` to a nice human-friendly format by appending one of `Kilo`,
    `Mega`, `Giga`, `Tera`, `Peta`, or `Eta` suffix.

    """
    tails = " KMGTPE"
    order, highest = 0, len(tails) - 1
    while (size >= 1024) and (order < highest):
        size /= 1024
        order += 1
    res = ("%.2f" % size).rstrip("0").rstrip(".")
    return "%s%s" % (res, tails[order])


def stat(path):
    """
    Return file or file system status.

    This is the same as the function ``os.stat`` but raises no error.
    """
    try:
        return os.stat(path)
    except os.error:
        return None


def lstat(path):
    """Same as `os.lstat`, but raises no error."""
    try:
        return os.lstat(path)
    except os.error:
        return None


def set_stat(fname, stat_info):
    os.chmod(fname, stat_info.st_mode)
    os.chown(fname, stat_info.st_uid, stat_info.st_gid)
    os.utime(fname, (stat_info.st_atime, stat_info.st_mtime))


def read_file(path):
    """Read a full file content and return an string."""
    try:
        with open(path, "r") as f:
            return f.read()
    except OSError:
        return ""


def listdir(path):
    """Same as ``os.listdir`` but normalizes `path` and raises no error."""
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
    elif pattern:
        for item in _list_one(pattern):
            yield item
    else:
        yield ("", lstat(os.curdir))


def imap(func, pattern):
    r"""Yields `func(file_0, stat_0)`, `func(file_1, stat_1)`, ... for each dir
    path. The `pattern` may contain:

    - Simple shell-style wild-cards à la `fnmatch`.

    - Regex if pattern starts with '(?'. Expressions must be valid, as
      in "(?:[^.].*)$" or "(?i).*\.jpe?g$". Remember to add the end mark '$'
      if needed.

    """
    for item, st in _list(pattern):
        res = func(item, st)
        if res is not None:
            yield res


def walk_up(start, sentinel):
    """Given a `start` directory walk-up the file system tree until either the
    FS root is reached or the `sentinel` is found.

    The `sentinel` must be a string containing the file name to be found.

    .. warning:: If `sentinel` is an absolute path that exists this will return
       `start`, no matter what `start` is (in windows this could be even
       different drives).

    If `start` path exists but is not a directory an OSError is raised.

    """
    from os.path import abspath, dirname, exists, isdir, join

    current = abspath(start)
    if not exists(current) or not isdir(current):
        raise OSError('Invalid directory "%s"' % current)
    previouspath = None
    found = False
    while not found and current is not previouspath:
        clue = join(current, sentinel)
        if exists(clue):
            found = True
        else:
            previouspath = current
            current = dirname(current)
    return current if found else None


from os import makedirs


def ensure_filename(filename, yields=False):
    """Ensures the existence of a file with a given filename.

    If the filename is taken and is not pointing to a file (or a link to a
    file) an OSError is raised.  If `exist_ok` is False the filename must not
    be taken; an OSError is raised otherwise.

    The function creates all directories if needed. See `makedirs`:func: for
    restrictions.

    If `yields` is True, returns the file object.  This way you may open a
    file for writing like this::

      with ensure_filename('/tmp/good-name-87.txt', yields=True) as fh:
          fh.write('Do it!')

    The file is open in mode 'w+b'.

    .. versionadded:: 1.6.1  Added parameter `yield`.

    """
    if not os.path.exists(filename):
        filename = normalize_path(filename)
        dirname = os.path.dirname(filename)
        makedirs(dirname, exist_ok=True)
        # TODO: Better hanlding of mode for reading/writing.
        fh = open(filename, "w+b")
        if not yields:
            fh.close()
        else:
            return fh
    else:
        if not os.path.isfile(filename):
            raise OSError("Expected a file but another thing is found '%s'" % filename)


def concatfiles(*files):
    """Concat several files to a single one.

    Each positional argument must be either:

    - a file-like object (ready to be passed to `shutil.copyfileobj`:func:)

    - a string, the file path.

    The last positional argument is the target.  If it's file-like object it
    must be open for writing, and the caller is the responsible for closing
    it.

    Alternatively if there are only two positional arguments and the first is
    a collection, the sources will be the members of the first argument.

    """
    import shutil

    from xotl.tools.params import check_count
    from xotl.tools.values.simple import force_iterable_coerce

    check_count(files, 2, caller="concatfiles")
    if len(files) == 2:
        files, target = force_iterable_coerce(files[0]), files[1]
    else:
        files, target = files[:-1], files[-1]
    if isinstance(target, str):
        target, opened = open(target, "wb"), True
    else:
        opened = False
    try:
        for f in files:
            if isinstance(f, str):
                fh = open(f, "rb")
                closefh = True
            else:
                fh = f
                closefh = False
            try:
                shutil.copyfileobj(fh, target)
            finally:
                if closefh:
                    fh.close()
    finally:
        if opened:
            target.close()


del sys
