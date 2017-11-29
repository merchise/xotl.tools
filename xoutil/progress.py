#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Tool to show a progress percent in the terminal.'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


__all__ = ['Progress']


_HELIX = '|/-\\'


class Progress(object):
    '''
    Print a progress percent to the console. Also the elapsed and the
    estimated times.

    To signal an increment in progress just call the instance and (optionally)
    pass a message like in::

        progress = Progress(10)
        for i in range(10):
            progress()
    '''

    def __init__(self, max_value=100, delta=1, first_message=None,
                 display_width=None):
        from xoutil.future.datetime import datetime
        self.max_value = max_value
        self.delta = delta
        self.percent = self.value = 0
        self.start_time = datetime.now()
        self.first_message = first_message
        self.display_width = display_width

    def __call__(self, progress=None, message='...'):
        if self.first_message is not None:
            print(self.first_message)
            self.first_message = None
        if progress is None:
            self.value += self.delta
        else:
            self.value = progress
        percent = 100 * self.value // self.max_value
        if self.percent != percent:
            import sys
            from xoutil.future.datetime import strfdelta
            self.percent = percent
            helix = _HELIX[percent % len(_HELIX)]
            elapsed = self.start_time.now() - self.start_time
            _cls = type(elapsed)
            total = _cls(seconds=elapsed.total_seconds() * 100 / self.percent)
            _fmt = '\r{helix} {percent}% - "{elapsed}" of about "{total}"'
            progress_line = _fmt.format(helix=helix, percent=percent,
                                        elapsed=strfdelta(elapsed),
                                        total=strfdelta(total))
            max_width = self.display_width or self._get_terminal_width()
            _fmt = ('{message: >%d}' % (max_width - len(progress_line) - 1))
            progress_line += _fmt.format(message=message)
            print(progress_line, end=('' if percent != 100 else '\n\r'))
            sys.stdout.flush()

    def _get_terminal_width(self, default=120):
        import os
        try:
            return int(os.environ.get('COLUMNS', default))
        except ValueError:
            return default
