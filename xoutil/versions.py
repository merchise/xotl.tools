#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.versions
# ---------------------------------------------------------------------
# Copyright (c) 2016-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-04-28

'''Versions API

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

from xoutil.decorator import singleton

try:
    _str_types = (str, unicode)
except:
    _str_types = (str,)


def _safe_int(arg):
    try:
        if isinstance(arg, _str_types):
            return int(arg)
        else:
            return arg
    except ValueError:
        return arg


def _crucial_parts(info):
    '''Count the important parts (starting integers) of a version info'''
    i, ok = 0, True
    while i < len(info) and ok:
        v = info[i]
        if isinstance(v, int):
            yield v
            i += 1
        else:
            ok = False


def _check(info):
    '''Check a version info.

    `info` could be a string or any iterable.  if `hard`, the 3 required
    integer components must be supplied at the beginning.

    '''
    import re
    from collections import Mapping, Set
    MAX_IDX = 3
    if isinstance(info, int):
        res = (info, )
    elif isinstance(info, float):
        res = tuple(int(i) for i in str(info).split('.'))
    elif isinstance(info, _str_types):
        try:
            res = (int(info), )
        except ValueError:
            regex = re.compile('^(\d+)(?:[.](\d+))?(?:[.](\d+))?')
            m = regex.match(info)
            if m:
                res = tuple(int(g) for g in m.groups() if g is not None)
            else:
                raise TypeError('version info check got an invalid string')
    else:
        # a valid iterable
        if not isinstance(info, (Mapping, Set)):
            try:
                res = tuple(_safe_int(c) for c in info)
            except TypeError:
                res = None
        else:
            res = None
        if res is None:
            # TODO: from xoutil.eight import type_name
            msg = 'version info check got an value of type "{}"'
            raise TypeError(msg.format(caller), type(info).__name__)
    return res


class ThreeNumbersVersion(tuple):
    '''A more structured version info for packages.

    This class can't be instanced, each sub-class must be treated as
    singleton.  Must be a tuple with three first components as integers
    'major', 'minor', and 'micro'.  Any custom implementation could have extra
    components.

    Instances of this class can be compared with a variety of value types:

    - An integer with the 'major' component.

    - A float with the ('major', 'minor') components.

    - A string is converted to a version tuple before compare it.

    .. versionadded:: 1.8.0

    '''
    def __new__(cls, info):
        return super(ThreeNumbersVersion, cls).__new__(cls, _check(info))

    @property
    def major(self):
        return self[0]

    @property
    def minor(self):
        return self[1]

    @property
    def micro(self):
        return self[2]

    def to_float(self):
        return float('{}.{}'.format(*self[:2]))

    def __eq__(self, other):
        from sys import version_info
        if isinstance(other, int):
            return self.major == other
        elif isinstance(other, _str_types + (float, )):
            return self.__eq__(tuple(str(other).split(' ')[0].split('.')))
        elif isinstance(other, ThreeNumbersVersion) or other is version_info:
            return True
        elif isinstance(other, (tuple, list)):
            MAX_IDX = 3
            count = len(other)
            if 1 <= count <= MAX_IDX:
                this = self[:count]
                other = tuple(int(c) for c in other)
                return this == other
            else:
                msg = 'Expecting from 1 to {} components; got {}'
                raise ValueError(msg.format(MAX_IDX, count))
        else:
            return NotImplemented

    def __lt__(self, other):
        import sys
        if isinstance(other, int):
            return self.__lt__((other,))
        elif isinstance(other, _str_types + (float, )):
            return self.__lt__(tuple(str(other).split(' ')[0].split('.')))
        elif isinstance(other, ThreeNumbersVersion) or other is sys.version_info:
            return False
        elif isinstance(other, (tuple, list)):
            MAX_IDX = 3
            count = len(other)
            if 1 <= count <= MAX_IDX:
                this = self[:MAX_IDX]
                other = tuple(int(c) for c in other)    # JIC strings are used
                return this < other
            else:
                msg = 'Expecting from 1 to {} components; got {}'
                raise ValueError(MAX_IDX, msg.format(len(other)))
        else:
            return NotImplemented

    def __gt__(self, other):
        import sys
        if isinstance(other, int):
            return self.__gt__((other,))
        elif isinstance(other, _str_types + (float, )):
            return self.__gt__(tuple(str(other).split(' ')[0].split('.')))
        elif isinstance(other, ThreeNumbersVersion) or other is sys.version_info:
            return False
        elif isinstance(other, (tuple, list)):
            MAX_IDX = 3
            count = len(other)
            if 1 <= count <= MAX_IDX:
                this = self[:MAX_IDX]
                other = tuple(int(c) for c in other)    # JIC strings are used
                return this > other
            else:
                msg = 'Expecting from 1 to {} components; got {}'
                raise ValueError(MAX_IDX, msg.format(len(other)))
        else:
            return NotImplemented

    def __ne__(self, other):
        return not (self == other)

    def __le__(self, other):
        return not (self > other)

    def __ge__(self, other):
        return not (self < other)


@singleton
class python_version(ThreeNumbersVersion):
    '''Current Python version.

    Initialized with `~sys.version_info`:obj: 5 components tuple.

    Extra components (besides 'major', 'minor', and 'micro') are:
    'releaselevel' (a string that could be 'alpha', 'beta', 'candidate', or
    'final'), and 'serial' (an integer).  The attribute 'pypy' could be used
    to determine if this is a PyPy instance or not.

    '''
    def __new__(cls):
        import sys
        self = ThreeNumbersVersion.__new__(cls, sys.version_info)
        self.pypy = sys.version.find('PyPy') >= 0
        return self

    @property
    def releaselevel(self):
        return self[3]

    @property
    def serial(self):
        return self[4]


def _get_mod_version(mod):
    '''Get a valid version from a module.

    Used internally by `PackageVersion`:class:.

    '''
    valid_names = ('VERSION_INFO', 'VERSION', 'version_info', 'version',
                   '__VERSION__', '__version__')
    i = 0
    res = None
    while res is None and i < len(valid_names):
        name = valid_names[i]
        version = getattr(mod, name, None)
        if version is not None:
            try:
                res = _check(version)
            except:
                pass
        i += 1
    return res


class PackageVersion(ThreeNumbersVersion):
    '''Current Package version.

    Extra components (besides 'major', 'minor', and 'micro') are:
    'releaselevel' (a string that could be 'alpha', 'beta', 'candidate', or
    'final'), and 'serial' (an integer).  The attribute 'pypy' could be used
    to determine if this is a PyPy instance or not.

    '''
    def __new__(cls, package_name):
        info = cls._find_version(package_name)
        if info:
            return super(PackageVersion, cls).__new__(cls, info)
        else:
            msg = '{}() could not determine a valid version'
            raise TypeError(msg.format(cls.__name__))

    @staticmethod
    def _find_version(package_name):
        res = None
        while not res and package_name:
            try:
                import pkg_resources
                dist = pkg_resources.get_distribution(package_name)
                try:
                    res = dist.parsed_version.base_version
                except:
                    res = dist.version
            except:
                from importlib import import_module
                try:
                    mod = import_module('.'.join((package_name, 'release')))
                    res = _get_mod_version(mod)
                except:
                    try:
                        mod = import_module(package_name)
                        res = _get_mod_version(mod)
                    except:
                        mod = __import__(package_name)
                        res = _get_mod_version(mod)
            if not res:
                aux = package_name.rsplit('.', 1)
                if len(aux) > 1:
                    package_name = aux[0]
        return res
