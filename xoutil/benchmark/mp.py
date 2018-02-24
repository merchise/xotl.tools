#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2013-2017 Merchise Autrement [~º/~] and Contributors
# Copyright (c) 2012 Manuel Vazquez

# TODO:  Take this out of xoutil.
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from multiprocessing import Pool, cpu_count
from itertools import count, islice, repeat

try:
    from itertools import izip as zip
except ImportError:
    pass


def gcd(a, b):
    while a % b != 0:
        a, b = b, a % b
    return b


def job(args):
    which, show = args
    try:
        result = gcd(which, which + 2 ** 37 - 73)
        if show and result != 1:
            print(which, result)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    from datetime import datetime
    import argparse

    cpus = max(cpu_count() - 1, 1)
    parser = argparse.ArgumentParser('Run several workers calculating GCD '
                                     'for large numbers. Uses multiprocessing '
                                     'to test several CPUs.')
    parser.add_argument('--show', help='Whether to print or not the gcds',
                        action='store_true', dest='show', default=False)
    parser.add_argument('--workers',
                        help='Number of workers. Defaults to %d.' % cpus,
                        type=int, action='store', dest='workers',
                        default=cpus)
    parser.add_argument('--size',
                        help='The magnitude of the test. Represents how many '
                             'cycles are processed, exactly 10**MAGNITUDE; '
                             'so be nice!', type=int, action='store',
                        dest='magnitude', default=6)
    args = parser.parse_args()

    pool = Pool(processes=args.workers)
    start = datetime.now()
    try:
        print('Working...')
        pool.imap(job, zip(islice(count(2 ** 1028 + 1), 10 ** args.magnitude),
                           repeat(args.show)), chunksize=1024)
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        pool.terminate()
        pool.join()
    end = datetime.now()
    total_seconds = (end - start).total_seconds()
    print('All workers (%d) finished in %f seconds' %
          (args.workers, total_seconds))
