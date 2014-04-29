#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_bases
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-03-25

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

import unittest
import random

from xoutil.bases import B32, B64


def build_many_tests():
    def test_many_random_convertions(self):
        subjects = [B32, B64]
        for _ in range(5):
            testcase = random.randrange(0, 2**128)
            subject = random.choice(subjects)
            assert testcase ==  subject.basetoint(subject.inttobase(testcase))
    return {'test_many_random_convertions_%d' % i:
            test_many_random_convertions for i in range(10)}

_TestManyConvertions = type(str('TestManyConvertions'),
                           (object, ),
                           build_many_tests())

class TestManyConvertions(unittest.TestCase, _TestManyConvertions):
    pass
