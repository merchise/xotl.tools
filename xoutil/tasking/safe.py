#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Python context with thread-safe queued data.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


# TODO: Optimize this by using standard threading locks
class SafeData:
    '''Python context with queued data.'''
    __slots__ = ('queue', 'timeout', 'data',)

    def __init__(self, data, timeout=None):
        from xoutil.eight.queue import Queue
        self.queue = Queue(1)
        self.queue.put(data)
        self.timeout = timeout
        self.data = data

    def __enter__(self):
        res = self.queue.get(True, self.timeout)
        if res is self.data:
            return res
        else:
            raise RuntimeError('unexpected error, invalid queued data')

    def __exit__(self, exc_type, exc_value, traceback):
        data = self.data
        self.queue.task_done()
        self.queue.put(data, True, self.timeout)
        return False
