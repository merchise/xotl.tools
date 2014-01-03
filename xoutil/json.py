# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.json
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
#
# Created on Jul 1, 2011

'''Extensions to the `json` standard library module.

It just adds the ability to encode/decode datetimes. But you should use the
JSONEncoder yourself.


You may use this module as drop-in replacement to Python's `json`.

'''

# TODO: consider use IoC to extend python json module

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from xoutil.modules import copy_members as _copy_python_module_members
_pm = _copy_python_module_members()

load = _pm.load

from xoutil.names import strlist as strs
__all__ = strs('file_load')
__all__.extend(getattr(_pm, '__all__', dir(_pm)))
del strs, _copy_python_module_members


class JSONEncoder(_pm.JSONEncoder):
    __doc__ = (_pm.JSONEncoder.__doc__ +
    '''
    Datetimes:

    We also support `datetime` values, which are translated to strings using
    ISO format.
    ''')

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def default(self, o):
        from decimal import Decimal as _Decimal
        from xoutil.types import is_iterable
        from xoutil.datetime import (is_datetime as _is_datetime,
                                     new_datetime as _new_datetime,
                                     is_date as _is_date,
                                     new_date as __new_date,
                                     is_time as _is_time)

        if _is_datetime(o):
            d = _new_datetime(o)
            return d.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif _is_date(o):
            d = __new_date(o)
            return d.strftime(self.DATE_FORMAT)
        elif _is_time(o):
            return o.strftime(self.TIME_FORMAT)
        elif isinstance(o, _Decimal):
            return str(o)
        elif is_iterable(o):
            return list(iter(o))
        return super(JSONEncoder, self).default(o)


def file_load(filename):
    with file(filename, 'r') as f:
        return load(f)


del _pm
