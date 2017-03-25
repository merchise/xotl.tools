#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.fp.cl
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-03-25

'''Common Lisp "reward" features.

John McCarthy and his students began work on the first Lisp implementation in
1958.  After FORTRAN, Lisp is the oldest language still in use.

Programmers who know Lisp will tell you, there is something about this
language that sets it apart.

.. versionadded:: 1.8.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.symbols import boolean


class logical(boolean):
    '''Represent Common Lisp two special values `t` and `nil`.

    Include redefinition of `__call__`:meth: to check values with special
    semantic:

    - When called as ``t(arg)``, check if `arg` is not `nil` returning a
      logical true: the same argument if `arg` is nil or a true boolean value,
      else return `t`.  That means that `False` or `0` are valid true values
      for Common Lisp but not for Python.

    - When called as ``nil(arg)``, check if `arg` is `nil` returning `t` or
      `nil` if not.

    Constructor could receive a valid name ('nil' or 't') or any other
    ``boolean`` instance.

    '''
    __slots__ = ()
    _valid = {'nil': False, 't': True}

    def __new__(cls, arg):
        from xoutil.symbols import boolean
        from xoutil import Undefined as wrong
        name = ('t' if arg else 'nil') if isinstance(arg, boolean) else arg
        value = cls._valid.get(name, wrong)
        if value is not wrong:
            return super(logical, cls).__new__(cls, name, value)
        else:
            msg = 'retrieving invalid logical instance "{}"'
            raise TypeError(msg.format(arg))

    def __call__(self, arg):
        if self:    # self is t
            return arg if arg or arg is nil else self
        else:    # self is nil
            return t if arg is self else self


nil, t = logical('nil'), logical('t')
