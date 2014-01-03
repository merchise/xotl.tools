#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_collections
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
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
try:
    import pytest
except:
    class pytest(object):
        class _mark(object):
            def __getattr__(self, attr):
                return lambda *a, **kw: (lambda f: f)
        mark = _mark()

from xoutil.collections import defaultdict

__docstring_format__ = 'rst'
__author__ = 'manu'


class TestCollections(unittest.TestCase):
    def test_defaultdict(self):
        d = defaultdict(lambda key, d: 'a')
        self.assertEqual('a', d['abc'])
        d['abc'] = 1
        self.assertEqual(1, d['abc'])


@pytest.mark.xfail(str("sys.version.find('PyPy') != -1"))
def test_stacked_dict():
    from xoutil.collections import StackedDict
    sd = StackedDict(a='level-0')
    sd.push(a=1, b=2, c=10)
    assert sd.level == 1
    sd.push(b=4, c=5)
    assert sd.level == 2
    assert sd['b'] == 4
    assert sd['a'] == 1
    assert sd['c'] == 5
    assert len(sd) == 3
    del sd['c']
    try:
        del sd['c']
        assert False, 'Should have raise KeyError'
    except KeyError:
        pass
    except:
        assert False, 'Should have raise KeyError'
    assert sd.pop() == {'b': 4}
    assert sd['b'] == 2
    assert sd['a'] == 1
    assert len(sd) == 3
    sd.pop()
    assert sd['a'] == 'level-0'
    try:
        sd.pop()
        assert False, 'Level 0 cannot be poped. It should have raised a TypeError'
    except TypeError:
        pass
    except:
        assert False, 'Level 0 cannot be poped. It should have raised a TypeError'


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(verbosity=2)
