#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)


def test_shadowed_dict_get():
    from xoutil.versions import python_version
    if python_version == 2:
        from xoutil.future.inspect import (_shadowed_dict, _static_getmro,
                                           _objclass, _sentinel)

        def _old_shadowed_dict(klass):
            if isinstance(klass, type):
                dict_get = type.__dict__["__dict__"].__get__
            else:
                def dict_get(item):
                    return {'__dict__': item.__dict__}
            for entry in _static_getmro(klass):
                try:
                    class_dict = dict_get(entry)["__dict__"]
                except KeyError:
                    pass
                else:
                    from xoutil.future.types import GetSetDescriptorType
                    if not (type(class_dict) is GetSetDescriptorType and
                            class_dict.__name__ == "__dict__" and
                            _objclass(class_dict, entry)):
                        return class_dict
            return _sentinel

        class OldClass:
            attr = _sentinel

        class Foobar(dict, OldClass):
            pass

        # New implementation
        assert _shadowed_dict(Foobar)['attr'] is _sentinel

        try:
            if _old_shadowed_dict(Foobar)['attr'] is _sentinel:
                # odd migrated behavior using old clases as bases
                assert False, 'This must have failed'
        except TypeError:
            assert True
