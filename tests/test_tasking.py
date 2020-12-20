#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import pytest
from xotl.tools.tasking import retry


class FailingMock:
    def __init__(self, start=0, threshold=5, sleeper=0):
        self.start = start
        self.threshold = threshold
        self.sleeper = sleeper

    def __call__(self, incr=1):
        if self.sleeper:
            import time

            time.sleep(self.sleeper)
        self.start += incr
        if self.start < self.threshold:
            raise ValueError(self.start)
        else:
            return self.start


def test_retrying_max_tries_not_enough_tries():
    fn = FailingMock(threshold=1000000, sleeper=0.5)
    with pytest.raises(ValueError):
        retry(fn, max_tries=3)


def test_retrying_max_tries_enough_tries():
    fn = FailingMock()
    assert retry(fn, max_tries=10) == 5


def test_retrying_max_time_runout():
    fn = FailingMock(threshold=1000000, sleeper=0.2)
    with pytest.raises(ValueError):
        retry(fn, max_time=0.3)


def test_retrying_max_time():
    fn = FailingMock(sleeper=0.2)
    assert retry(fn, max_time=0.2 * 5) == 5


def test_signature():
    fn = FailingMock()
    with pytest.raises(TypeError):
        assert retry(fn, (), {}, 5)
    with pytest.raises(TypeError):
        assert retry(fn, (), {}, x=5)
