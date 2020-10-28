#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xotl.tools.tasking.safe import SafeData


def test_safe():
    from xotl.tools.future.threading import async_call
    from time import sleep

    data = {}
    qd = SafeData(data, timeout=5.0)

    def inner(name, start, end):
        step = 1 if start < end else -1
        for i in range(start, end, step):
            with qd as d:
                d[i] = d.get(i, 0) + 1
            sleep(0.001 * i)
        with qd as d:
            d[name] = True

    one, two = "one", "two"
    async_call(inner, args=[one, 1, 6])
    async_call(inner, args=[two, 8, 3])
    finish = {one: False, two: False}
    while not (finish[one] and finish[two]):
        with qd as d:
            for k in (one, two):
                if d.get(k):
                    finish[k] = True
        sleep(0.001)
    aux = {i: 1 for i in range(1, 6)}
    for i in range(8, 3, -1):
        aux[i] = aux.get(i, 0) + 1
    aux[one] = aux[two] = True
    assert data == aux
