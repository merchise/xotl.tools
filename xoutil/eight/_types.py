#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Some functions implemented in module ``types`` in Python 3 but not in
Python 2 needed for '_meta*' implementation.

'''
__all__ = ['new_class', 'prepare_class', 'get_exec_body']


from types import new_class, prepare_class  # noqa
from types import MappingProxyType  # noqa


def get_exec_body(**kwargs):
    '''Return an `exec_body` function that update `ns` with `kwargs`.'''
    def exec_body(ns):
        ns.update(kwargs)
        return ns
    return exec_body
