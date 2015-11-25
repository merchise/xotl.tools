#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# tests.test_params
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
from xoutil.params import ParamConformer


from xoutil.eight import string_types
from xoutil.cl import file_coerce, positive_int_coerce

sample_scheme = {
    'stream': (file_coerce, {0, 3}, {'output'}, sys.stdout),
    'indent': (positive_int_coerce, {1}, 1),
    'width': (positive_int_coerce, {2}, {'max_width'}, 79),
    'newline': (string_types, '\n'), }

del file_coerce, positive_int_coerce, string_types


def test_basic_params():
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


def test_param_errors():
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
    conformer = ParamConformer(sample_scheme, __strict__=True)
    try:
        get_values(80, indent=4, extra="I'm not OK!")
        assert False, 'Should raise ValueError'
    except ValueError:
        pass
    except:
        assert False, 'Should have raised an ValueError'
