#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Standardization of Queue Processing.

In Python 2, the Queue processing module (A multi-producer, multi-consumer
queue) has the name with initial capital letter, nevertheless in Python 3 the
name is all in lower-case.

This is a compatibility module, importing symbols from this will be the same
in both versions of Python.

In Python 3 module there are two symbols imported from ``heapq`` module, those
are imported here for full compatibility.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

try:
    from Queue import (Queue, LifoQueue, PriorityQueue, Empty, Full)    # noqa
except ImportError:
    from queue import (Queue, LifoQueue, PriorityQueue, Empty, Full)    # noqa

try:
    from heapq import (heappop, heappush)    # noqa
except ImportError:
    from queue import (heappop, heappush)    # noqa

# best available implementation of current time in seconds
import time as _time

time = getattr(_time, 'monotonic', _time.time)

del _time
