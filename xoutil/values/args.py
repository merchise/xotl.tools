#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.values.args
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-09-06

'''Simple function argument validator.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from xoutil import Unset


def param_get(args, kwargs, idx, name, default=Unset, coercers=Unset):
    '''Get an argument value that could be given by order or by name.

    :param args: A tuple -or list- with positional arguments as received in a
           function for a parameter declared as ``*args``.

    :param kwargs: A dictionary with named arguments as received in a function
           for a parameter declared as ``**kwargs``.

    :param idx: Index of positional argument.  If None, the requested argument
           value could only be given as a named argument.

    :param name: The name of a named argument.  if None, this argument could
           only be given as a positional argument.

    :param default: Optional default value to return it if no positional or
           named argument is found.

    :param coercers: A collection of functions, each one to transform or
           validate the value being returned.

    '''
    in_args = idx is not None and (0 <= idx < len(args))
    in_kwargs = name in kwargs
    count = in_args + in_kwargs
    if count == 0:
        res = default
    elif count == 1:
        res = args[idx] if in_args else kwargs[name]
    else:    # count == 2: error; both, positional and by name, are given
        res = Unset
    if res is not Unset:
        if coercers is Unset:
            return res
        else:
            from . import compose
            coercer = compose(coercers)
            return coercer(res)
    else:
        msg = ('Expecting exactly one occurrence for argument '
               '(idx: {}, name: {!r}); but {} was processed.')
        raise TypeError(msg.format(idx, name, count))
