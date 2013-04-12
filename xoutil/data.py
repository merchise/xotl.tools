# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.data
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# Copyright (c) 2009-2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.

'''Some useful Data Structures and data-related algorithms and functions.'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_absimports)

import xoutil.collections
from xoutil.deprecation import deprecated

def smart_copy(source, target, full=False):
    '''Copies attributes (or keys) from `source` to `target`.

    Names starting with an '_' will not be copied unless `full` is True.

    When `target` is not a dictionary (other Python objects):

        - Only valid identifiers will be copied.

        - If `full` is False only public values (which name does not starts
          with '_') will be copied.

    Assumed introspections:

        - `source` is considered a dictionary when it has a method called
          ``iteritem`` or ``items``.

        - `target` is considered a dictionary when: ``isinstance(target,
          collections.Mapping)`` is True.

    '''
    from collections import Mapping
    from xoutil.validators.identifiers import is_valid_identifier
    if callable(getattr(source, 'iteritems', None)):
        items = source.iteritems()
    elif callable(getattr(source, 'items', None)):
        items = source.items()
    else:
        items = ((name, getattr(source, name)) for name in dir(source))
    if isinstance(target, Mapping):
        def setvalue(key, value):
            target[key] = value
    else:
        def setvalue(key, value):
            if is_valid_identifier(key) and (full or not key.startswith('_')):
                setattr(target, key, value)
    for key, value in items:
        setvalue(key, value)


def adapt_exception(value, **kwargs):
    '''Like PEP-246, Object Adaptation, with ``adapt(value, Exception)``.'''
    isi, issc, ebc = isinstance, issubclass, Exception
    if isi(value, ebc) or issc(value, ebc):
        return value
    elif isi(value, (tuple, list)) and len(value) > 0 and issc(value[0], ebc):
        from xoutil.compat import str_base
        iss = lambda s: isinstance(s, str_base)
        ecls = value[0]
        args = ((x.format(**kwargs) if iss(x) else x) for x in value[1:])
        return ecls(*args)
    else:
        return None


@deprecated(xoutil.collections.SmartDict)
class SmartDict(xoutil.collections.SmartDict):
    '''A smart dict that extends the `update` method to accept several args.

    .. warning:: Deprecated, moved to :class:`xoutil.collections.SmartDict`.

                 Deprecated since 1.3.1

    '''

@deprecated(xoutil.collections.OrderedSmartDict)
class SortedSmartDict(xoutil.collections.OrderedSmartDict):
    '''An ordered SmartDict.

    .. warning:: Deprecated, moved to
                :class:`xoutil.collections.OrderedSmartDict`.

                 Deprecated since 1.3.1

    '''
