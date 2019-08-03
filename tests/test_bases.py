#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import unittest
import random

from xotl.tools.bases import B32, B64, B64symbolic


def build_many_tests():
    def test_many_random_convertions(self):
        subjects = [B32, B64, B64symbolic]
        for _ in range(5):
            testcase = random.randrange(2 ** 64, 2 ** 128)
            subject = random.choice(subjects)
            assert testcase == subject.basetoint(subject.inttobase(testcase))

    return {
        "test_many_random_convertions_%d" % i: test_many_random_convertions
        for i in range(10)
    }


_TestManyConvertions = type(str("TestManyConvertions"), (object,), build_many_tests())


class TestManyConvertions(unittest.TestCase, _TestManyConvertions):
    def test_regression_56107046767814579580835126010035242071(self):
        number = 56107046767814579580835126010035242071
        b64 = B64symbolic
        assert number == b64.basetoint(b64.inttobase(number))
