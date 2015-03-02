#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.clutter
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created 2015-02-25

'''Portable serialization for Python objects.

Main class `Clutter` serialize/deserialize Python objects to/from strings
using `dconf` and `gconf` conventions:

- Classes (`uint16`, `uint32`, `uint64`, `boolean`).

- Standard Python functions `repr` and `eval` as counterpart for simple
  serialization.

- Pickle module for more complex or structured objects.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

from xoutil import Unset


__docstring_format__ = 'rst'


class Clutter(object):
    '''Main class for portable serialization of Python objects.

    Functions:

    dumps(object) -> string

    loads(string) -> object

    The name comes from the verb meaning of the word "fill a space in a
    disorderly way".

    '''

    def _get_globals():
        '''WTF: Now I remember why real anonymous functions are needed.'''
        from xoutil.datetime import (datetime, date, time)    # noqa
        from .values import (uint16, uint32, uint64)    # noqa
        from .values import (int16, int32, int64)    # noqa
        return dict(locals())

    _GLOBALS = _get_globals()

    del _get_globals

    def __init__(self, context=None):
        '''Initialize the clutter with a :param context: that will be used as
        local variables in :func:`eval` calls.

        You can update class variable `_GLOBALS` to change the value is used
        for `globals`.

        '''
        self.context = context

    def dumps(self, obj):
        '''Create the best string that could be decoded back to a Python
        object clone equivalent to argument `obj`.

        '''
        res = self.repr(obj)
        aux = self.eval(res)    # Check `res` validity
        if aux is not Unset:
            return res
        else:
            res = self.pickle(obj)
            aux = self.unpickle(res)    # Check `res` validity
            if aux is not Unset:
                return res
            else:
                msg = "Object of type `%s` can't be encoded!" % type(obj)
                raise TypeError(msg)

    def loads(self, str):
        '''Obtain a valid Python object from a serialized string.'''
        res = self.eval(str)
        if res is not Unset:
            return res
        else:
            res = self.unpickle(str)
            if res is not Unset:
                return res
            else:
                msg = "Invalid serialized string '%s'!" % str
                raise ValueError(msg)

    def repr(self, obj):
        '''Try to encode an object to a string value using simple `repr`.

        This method is the counterpart of :method:`eval`.

        Must returns always a valid string.

        '''
        value = repr(obj)
        if value.startswith('u"') or value.startswith("u'"):
            value = value[1:]    # Avoid unicode Python 2.x compatibility
        dtprefix = 'datetime.'
        if value.startswith(dtprefix):
            value = value[len(dtprefix):]
        return value

    def eval(self, value):
        '''Try to decode a string `value` using `eval`.

        Returns `Unset` if no object can be obtained.

        '''
        from xoutil.logical import Logical
        from xoutil.clutter.values import Prefixed
        try:
            res = Logical.parse(value)
            if res is None:
                res = Prefixed.parse(value)
                if res is Unset:
                    res = eval(value, self._GLOBALS, self.context)
        except:    # Check for module import
            import re
            from importlib import import_module
            ID = r'[_a-z][\w]*'
            RE = r'(?i)(?P<mod>{id}([.]{id})*)[.](?P<cls>{id})(?P<rest>.*)'
            regex = re.compile(RE.format(id=ID))
            match = regex.match(value)
            try:
                d = match.groupdict()
                mod = import_module(d['mod'])
                key = d['cls']
                cls = getattr(mod, key)
                ctx = dict(self.context or {})
                ctx.update({key: cls})
                res = eval(key + d['rest'], self._GLOBALS, ctx)
            except:
                res = Unset
        return res

    def pickle(self, obj):
        '''Try to encode Python object into a pickled string.

        Clutter uses a pickled string to store values that can't be evaluated
        as Python expressions.

        Returns `Unset` if no string can be obtained.

        '''
        from base64 import b64encode
        from pickle import dumps
        try:
            # Use protocol 2 for compatibility between Python 2 and 3
            s = dumps(obj, protocol=2)
            return b64encode(s)
        except:
            return Unset

    def unpickle(self, value):
        '''Try to decode a pickled string `value` into a Python object.

        Clutter uses a pickled string to store values that can't be evaluated
        as Python expressions.

        Returns `Unset` if no value can be obtained.

        '''
        from base64 import b64decode
        from pickle import loads
        try:
            if '#' in value:    # Remove comment
                value = value.split('#')[0].strip()
            s = b64decode(value)
            return loads(s)
        except:
            return Unset
