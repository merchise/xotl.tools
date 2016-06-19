#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.values
# ---------------------------------------------------------------------
# Copyright (c) 2015, 2016 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-07-15

'''Some generic coercers (or checkers) for value types.

This module coercion function are not related in any way to deprecated old
python feature, are similar to a combination of object mold/check:

- *Mold* - Fit values to expected conventions.

- *Check* - These functions must return `Invalid`\ [#pyni]_ special value to
  specify that expected fit is not possible.

.. [#pyni] We don't use Python classic `NotImplemented` special value in order
           to obtain False if the value is not coerced (`Invalid`).

A custom coercer could be created with closures, for an example see
`create_int_range_coerce`:func:.

Also contains sub-modules to obtain, convert and check values of common types.

.. versionadded:: 1.7.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


import warnings

warnings.warn('"xoutil.values" is now deprecated and it will be removed. Use '
              '"xoutil.cl" instead.', stacklevel=2)

del warnings

from xoutil.cl import (logical, nil, t, _coercer_decorator, vouch,    # noqa
                       MetaCoercer, coercer, coercer_name, identity_coerce,
                       void_coerce, type_coerce, types_tuple_coerce,
                       callable_coerce, file_coerce, float_coerce, int_coerce,
                       number_coerce, positive_int_coerce,
                       create_int_range_coerce, identifier_coerce,
                       full_identifier_coerce, names_coerce,
                       create_unique_member_coerce, sized_coerce, custom,
                       istype, typecast, safe, compose, some, combo, pargs,
                       iterable, mapping, ids, )


valid, Invalid, check = t, nil, vouch

# TODO: Migrate all uses of this module and remove it.
