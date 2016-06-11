#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight.queue
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-11-19

'''A multi-producer, multi-consumer queue.'''

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
