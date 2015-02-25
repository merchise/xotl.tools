# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# xoutil.sketch.tree
# ----------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
#
# @created: 2015-02-25


'''A tree of mappings.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)


from xoutil.objects import SafeDataItem as safe
from xoutil.collections import (OpenDictMixin, SmartDictMixin, MutableMapping,
                                OrderedDict)


class TreeDict(OpenDictMixin, SmartDictMixin, MutableMapping):
    '''A tree of mappings.

    Keys could be expressed as POSIX directory paths, each level will be
    stored in an inner instance of `TreeDict`.  Keys can be searched relative
    from current level ('..' and '.' special names can be used as in file
    names); or absolute, in which case the root level will be used to get
    values.

    This class uses POSIX conventions:

    - '.' for special current node name (See `posixpath.curdir`).

    - '..' for special parent node name (See `posixpath.pardir`).

    - '/' name path separator (See `posixpath.sep`).

    Properties:

    - :attr:`_dot_dot` returns the parent node

    - :attr:`_name` returns the current node name

    - :attr:`_full_name` returns the name from root

    - :attr:`_level` returns the integer level from current node to root

    .. versionchanged:: 1.6.8

    '''
    # TODO: Analyze Twitter social networks conventions: '@' prefix for user
    #       identifier; and '#' prefix for semantic classifier.

    __slots__ = (safe.slot('_name', default=None),
                 safe.slot('_dot_dot', default=None),
                 safe.slot('__inner', OrderedDict),
                 safe.slot(OpenDictMixin.__cache_name__, dict))

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    @property
    def _level(self):
        '''Return the current level number.

        The root level is 0.

        '''
        parent = self._dot_dot
        return parent._level + 1 if parent else 0

    @property
    def _parent(self):
        '''Alias for `_dot_dot` (parent node).'''
        return self._dot_dot

    @property
    def _full_name(self):
        '''Return the current node full-name.'''
        from posixpath import join, sep
        parent = self._dot_dot
        pfn, name = (parent._full_name, self.name) if parent else (sep, '')
        return join(pfn, name)

    def __str__(self):
        # TODO: Optimize
        return str(dict(self))

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, str(self))

    def __len__(self):
        return len(self.inner)

    def __iter__(self):
        return iter(self.inner)

    def __getitem__(self, key):
        return self.inner[key]

    def __setitem__(self, key, value):
        self.inner[key] = value

    def __delitem__(self, key):
        del self.inner[key]

    def dump(self, file):
        '''Write this tree dict in `dconf` format to the given file.'''
        import posixpath
        fn = self._full_name.strip(posixpath.sep)
        if fn:
            print('[%s]' % fn, file=file)
        trees = []
        for key in self:
            value = self[key]
            if isinstance(value, TreeDict):
                trees.append((key, value))
            else:
                value = None    # XXX: Incomplete
