# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight.types
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-02-25


'''Functions implemented in module `types` in Python 3 but not in Python 2.

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        # unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

import warnings

warnings.warn('"xoutil.eight.types" is now deprecated and it will be removed.'
              ' Use "xoutil.future.types" instead.', stacklevel=2)

del warnings

from xoutil.future.types import (NoneType, DictProxyType,    # noqa
                                 MappingProxyType, MemberDescriptorType,
                                 GetSetDescriptorType, SimpleNamespace,
                                 DynamicClassAttribute, new_class,
                                 prepare_class, _calculate_meta,
                                 get_exec_body)


__all__ = ['DictProxyType', 'MemberDescriptorType', 'NoneType',
           'MappingProxyType', 'SimpleNamespace', 'DynamicClassAttribute',
           'new_class', 'prepare_class']
