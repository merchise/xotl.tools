# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.progress
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# Copyright (c) 2011, 2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.

'''Tool to show a progress percent in the terminal.'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

from xoutil.names import strlist as strs
__all__ = strs('Progress')
del strs


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

    def __init__(self, max_value=100, delta=1, first_message=None):
        from xoutil.datetime import datetime
        self.max_value = max_value
        self.delta = delta
        self.percent = self.value = 0
        self.start_time = datetime.now()
        self.first_message = first_message

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
            from xoutil.datetime import strfdelta
            self.percent = percent
            helix = _HELIX[percent % len(_HELIX)]
            elapsed = self.start_time.now() - self.start_time
            total = type(elapsed)(seconds=elapsed.total_seconds() * 100 / self.percent)
            progress_line = '\r{helix} {percent}% - "{elapsed}" of about "{total}"'.format(
                         helix=helix,
                         percent=percent,
                         elapsed=strfdelta(elapsed),
                         total=strfdelta(total))
            max_width = self._get_terminal_width()
            progress_line += ('{message: >%d}' % (max_width - len(progress_line) - 1)).format(message=message)
            print(progress_line, end=('' if percent != 100 else '\n\r'))
            sys.stdout.flush()

    def _get_terminal_width(self, default=120):
        return default
