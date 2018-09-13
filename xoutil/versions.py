#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

# TODO: Document (version.rst) this module.  Add tests.
'''Versions API

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

from xoutil.decorator import singleton


def _check(info):
    '''Validate a version info.

    :param info: could be a string, an integer, float, or any integer
           collection (only first three valid integers are used).

    :returns: a valid tuple or an error if invalid.

    '''
    from itertools import takewhile
    from collections import Iterable
    from distutils.version import LooseVersion
    if isinstance(info, int):
        aux = (info,)
    elif isinstance(info, float):
        aux = LooseVersion(str(info)).version
    elif isinstance(info, str):
        aux = LooseVersion(str(info)).version
    elif isinstance(info, Iterable):
        aux = info
    else:
        aux = ()
    res = tuple(takewhile(lambda i: isinstance(i, int), aux))
    if 0 < len(res) <= 3:
        while res[-1] == 0 and len(res) > 1:
            res = res[:-1]
        return res
    else:
        raise ValueError("invalid version number '{}'".format(info))


class ThreeNumbersVersion(tuple):
    '''A more structured version info for packages.

    This class is mainly intended to be sub-classed as a singleton resulting
    in a tuple with three integer components as 'major', 'minor', and 'micro'.

    Instances of this class can be compared with a variety of value types:

    - An integer with the 'major' component.

    - A float with the ('major', 'minor') components.

    - A string is converted to a version tuple before compare it.

    Comparison only is relevant for heading integers.

    .. versionadded:: 1.8.0

    '''
    def __new__(cls, info):
        arg = _check(info)
        arg += tuple(0 for i in range(3 - len(arg)))
        return super().__new__(cls, arg)

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

    __float__ = to_float
    __trunc__ = major

    def __eq__(self, other):
        try:
            aux = _check(other)
            this = self[:len(aux)]
            return this == aux
        except Exception:
            return False

    def __lt__(self, other):
        try:
            aux = _check(other)
            count = len(self)
            this = self[:count]
            return this < aux
        except Exception:
            return NotImplemented

    def __gt__(self, other):
        try:
            aux = _check(other)
            count = len(self)
            this = self[:count]
            return this > aux
        except Exception:
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
        self = super().__new__(cls, sys.version_info)
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
            except TypeError:
                pass
        i += 1
    if not res:
        try:
            import os
            path = os.path.dirname(os.__file__)
            if mod.__file__.startswith(path):
                res = python_version
        except Exception:  # TODO: @med which exceptions?
            pass
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
            return super().__new__(cls, info)
        else:
            msg = '{}() could not determine a valid version'
            raise TypeError(msg.format(cls.__name__))

    @staticmethod
    def _find_version(package_name):
        if package_name in ('__builtin__', 'builtins'):
            return python_version
        else:
            res = None
            while not res and package_name:
                try:
                    import pkg_resources
                    dist = pkg_resources.get_distribution(package_name)
                    try:
                        res = dist.parsed_version.base_version
                    except AttributeError:
                        res = dist.version
                except Exception:  # TODO: @med which exceptions?
                    from importlib import import_module
                    try:
                        mod = import_module('.'.join(
                            (package_name, 'release')
                        ))
                        res = _get_mod_version(mod)
                    except ImportError:
                        try:
                            mod = import_module(package_name)
                            res = _get_mod_version(mod)
                        except ImportError:
                            mod = __import__(package_name)
                            res = _get_mod_version(mod)
                if not res:
                    aux = package_name.rsplit('.', 1)
                    package_name = aux[0] if len(aux) > 1 else ''
            return res
