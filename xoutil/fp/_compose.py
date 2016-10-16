#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.fp._compose
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-10-14

'''Function composition with full-argument passing.

See `xoutil.fp.tools`:mod: for standard `compose`.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


class pos_args(tuple):
    '''Mark variable number positional arguments (see `fargs`:class:).'''


class kw_args(dict):
    '''Mark variable number keyword arguments (see `fargs`:class:).'''


class full_args(tuple):
    '''Mark variable number arguments for composition.

    Pair containing positional and keyword ``(args, kwds)`` arguments.

    In standard functional composition, the result of a function is considered
    a single value to be use as the next function argument.  You can override
    this behaviour returning one instance of `pos_args`:class:,
    `kw_args`:class:, or this class; in order to provide multiple arguments to
    the next call.

    Since types are callable, you may use it directly in `compose`:func:
    instead of changing your functions to returns the instance of one of these
    classes::

      >>> def join_args(*args):
      ...     return ' -- '.join(str(arg) for arg in args)

      >>> compose(join_args, pos_args, list, range)(2)
      '0 -- 1'

      # Without 'pos_args', it prints the list
      >>> compose(join_args, list, range)(2)
      '[0, 1]'

    '''
    @staticmethod
    def parse(arg):
        '''Parse possible alternatives.

        If ``arg`` is:

        - a pair of a ``tuple`` and a ``dict``, return a `full_args`:class:
          instance.

        - a ``tuple`` or a ``list``, return a `pos_args`:class: instance;

        - a ``dict``, return a `kw_args`:class: instance;

        - ``None``, return an empty `pos_args`:class: instance.

        For example (remember that functions return 'None' when no explicit
        'return' is issued)::

          >>> def join_args(*args):
          ...     if args:
          ...         return ' -- '.join(str(arg) for arg in args)

          >>> compose(join_args, full_args.parse, join_args)()
          None

          # Without 'full_args.parse', return 'str(None)'
          >>> compose(join_args, join_args)()
          'None'

        '''
        if isinstance(arg, tuple):
            def check(pos, kw):
                return isinstance(pos, tuple) and isinstance(kw, dict)
            if len(arg) == 2 and check(*arg):
                return full_args(arg)
            else:
                return pos_args(arg)
        elif isinstance(arg, list):
            return pos_args(arg)
        elif isinstance(arg, dict):
            return kw_args(arg)
        elif arg is None:
            return pos_args()
        else:
            from xoutil.eight import typeof
            msg = 'Expecting None, a tuple, a list, or a dict; {} found'
            raise TypeError(msg.format(typeof(arg).__name__))


def compose(*funcs):
    '''Composition of several functions.

    Functions are composed right to left.  A composition of zero functions
    gives back the `identity`:func: function.

    Rules -inner `all`:func:- must be fulfilled::

      >>> x = 15
      >>> f, g, h = x.__add__, x.__mul__, x.__xor__
      >>> all((compose() is identity,
      ...      compose()(x) is x,
      ...      compose(f) is f,
      ...      compose(g, f)(x) == g(f(x)),
      ...      compose(h, g, f)(x) == h(g(f(x)))))
      True

    If any "intermediate" function returns an instance of:

    - `vargs`:class:\ : it's expanded as variable positional arguments to the
      next function.

    - `kvargs`:class:\ : it's expanded as variable positional and keyword
      arguments.

    Use `nargs`:func: to check if a previous result in the composition chain
    was procedural (``None``).

    '''
    count = len(funcs)
    if count == 0:
        return identity
    elif len(funcs) == 1:
        return funcs[0]
    else:
        def composed(*args, **kwds):
            i = len(funcs)
            res = full_args((args, kwds))
            while i > 0:
                i -= 1
                fn = funcs[i]
                if isinstance(res, pos_args):
                    res = fn(*res)
                elif isinstance(res, kw_args):
                    res = fn(**res)
                elif isinstance(res, full_args):
                    res = fn(*res[0], **res[1])
                else:
                    res = fn(res)
            return res
        if count <= 3:
            composed.__doc__ = cnames(*funcs)
        else:
            composed.__doc__ = '{} composed functions.'.format(count)
        del count
        return composed
