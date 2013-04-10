#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_collections
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Jul 3, 2012


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)

import unittest

from xoutil.collections import defaultdict

__docstring_format__ = 'rst'
__author__ = 'manu'


class TestCollections(unittest.TestCase):
    def test_defaultdict(self):
        d = defaultdict(lambda key, d: 'a')
        self.assertEqual('a', d['abc'])
        d['abc'] = 1
        self.assertEqual(1, d['abc'])


def test_stacked_dict():
    from xoutil.collections import StackedDict
    sd = StackedDict(a=1, b=2)
    assert sd.level == 1
    sd.push(b=4, c=5)
    assert sd.level == 2
    assert sd['b'] == 4
    assert sd['a'] == 1
    assert sd['c'] == 5
    assert len(sd) == 3
    del sd['c']
    assert sd.pop() == {'b': 4}
    assert sd['b'] == 2
    assert sd['a'] == 1
    assert len(sd) == 2


def test_stacked_dict_contextmanager():
    import pytest
    from xoutil.collections import StackedDict
    with StackedDict(a=1, b=2, c=6) as sd:
        assert sd.level == 2  # Since creating a stackdict is by default a
                              # level 1, entering as a context manager
                              # increments the level
        with sd:
            sd.update(b=4, c=5)
            assert sd['b'] == 4
            assert sd['a'] == 1
            assert sd['c'] == 5
            assert len(sd) == 3
            del sd['c']
            with pytest.raises(KeyError):
                sd['not']
            with pytest.raises(KeyError):
                del sd['c']  # Not in this level to erase
            assert sd['c'] == 6
        assert sd.b == 2   # It's an opendict
        assert sd['a'] == 1
        assert sd['c'] == 6
        assert len(sd) == 3

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(verbosity=2)
