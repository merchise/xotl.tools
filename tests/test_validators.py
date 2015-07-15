#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# tests.test_validators
#----------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2015-07-14

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

import sys
from xoutil.validators.args import ParamConformer, Invalid


from xoutil.eight import string_types


def check_file_like(arg):
    from xoutil.eight.io import is_file_like
    return arg if is_file_like(arg) else Invalid


def check_positive_int(arg):
    from xoutil.eight import integer_types, string_types
    if isinstance(arg, integer_types):
        return arg if arg >= 0 else Invalid
    elif isinstance(arg, string_types):
        try:
            arg = int(arg)
            return arg if arg >= 0 else Invalid
        except ValueError:
            return Invalid
    else:
        return Invalid

sample_scheme = {
    'stream': (check_file_like, {0, 3}, {'output'}, sys.stdout),
    'indent': (check_positive_int, {1}, 1),
    'width': (check_positive_int, {2}, {'max_width'}, 79),
    'newline': (string_types, '\n'), }

del check_file_like, check_positive_int, string_types


def test_basic_args():
    conformer = ParamConformer(sample_scheme)

    def get_values(*args, **kwargs):
        conformer(args, kwargs)
        return kwargs

    def foobar(**kwargs):
        from xoutil.eight import iteritems
        res = {key: ps['default'] for key, ps in iteritems(conformer.scheme)}
        for key, value in iteritems(kwargs):
            res[key] = value
        return res

    res = get_values(4, 80)
    assert get_values(4, 80) == foobar(indent=4, width=80)
    assert get_values(2) == foobar(indent=2)
    assert get_values(80, indent=4,
                      extra="I'm OK!") == foobar(width=80, indent=4,
                                                 extra="I'm OK!")
    assert get_values(width=80) == foobar(width=80)
    assert get_values(sys.stderr, 4, 80) == foobar(indent=4, width=80,
                                                   stream=sys.stderr)
    assert get_values(4, sys.stderr,
                      newline='\n\r') == foobar(indent=4, stream=sys.stderr,
                                                newline='\n\r')
    assert get_values(4, output=sys.stderr) == foobar(indent=4,
                                                      stream=sys.stderr)
    assert get_values(4, max_width=80) == foobar(indent=4, width=80)


def test_args_errors():
    conformer = ParamConformer(sample_scheme)

    def get_values(*args, **kwargs):
        conformer(args, kwargs)
        return kwargs

    try:
        get_values(sys.stderr, 4, output=sys.stderr)
        assert False, 'Should raise TypeError'
    except TypeError:
        pass
    except:
        assert False, 'Should have raised an TypeError'
    try:
        get_values(4, -79)
        assert False, 'Should raise TypeError'
    except TypeError:
        pass
    except:
        assert False, 'Should have raised an TypeError'
    conformer = ParamConformer(sample_scheme, strict=True)
    try:
        get_values(80, indent=4, extra="I'm OK!")
        assert False, 'Should raise ValueError'
    except ValueError:
        pass
    except:
        assert False, 'Should have raised an ValueError'
