# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight._types
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-06-10


'''Some functions implemented in module ``types`` in Python 3 but not in
Python 2 needed for '_meta*' implementation.

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)


__all__ = ['new_class', 'prepare_class']


try:
    from types import new_class
except ImportError:
    # PEP 3115 compliant dynamic class creation.  Used in
    # xoutil.objects.metaclass
    #
    # Taken from Python 3.3 code-base.
    def new_class(name, bases=(), kwds=None, exec_body=None):
        """Create a class object dynamically using the appropriate metaclass.

        """
        meta, ns, kwds = prepare_class(name, bases, kwds)
        if exec_body is not None:
            exec_body(ns)
        return meta(name, bases, ns, **kwds)


try:
    from types import prepare_class
except ImportError:
    def prepare_class(name, bases=(), kwds=None):
        """Call the __prepare__ method of the appropriate metaclass.

        Returns (metaclass, namespace, kwds) as a 3-tuple

        *metaclass* is the appropriate metaclass
        *namespace* is the prepared class namespace
        *kwds* is an updated copy of the passed in kwds argument with any
        'metaclass' entry removed. If no kwds argument is passed in, this will
        be an empty dict.

        """
        from . import typeof
        if kwds is None:
            kwds = {}
        else:
            kwds = dict(kwds)  # Don't alter the provided mapping
        meta = kwds.pop('metaclass', None)
        if not meta:
            meta = typeof(bases[0]) if bases else type
        if isinstance(meta, type):
            # when meta is a type, we first determine the most-derived
            # metaclass instead of invoking the initial candidate directly
            meta = _calculate_meta(meta, bases)
        if hasattr(meta, '__prepare__'):
            ns = meta.__prepare__(name, bases, **kwds)
        else:
            ns = {}
        return meta, ns, kwds


try:
    from types import _calculate_meta
except ImportError:
    # XXX: Remove all these `continue` statements
    def _calculate_meta(meta, bases):
        """Calculate the most derived metaclass."""
        from . import typeof, class_types
        old_cls = next((cls for cls in class_types if cls is not type), None)
        winner = meta
        for base in bases:
            base_meta = typeof(base)
            if issubclass(winner, base_meta):
                continue
            if issubclass(base_meta, winner):
                winner = base_meta
                continue
            # else:
            raise TypeError("metaclass conflict: the metaclass of a derived "
                            "class must be a (non-strict) subclass of the "
                            "metaclasses of all its bases")
        if winner is not old_cls:
            return winner
        else:
            msg = ("Error when calling the metaclass bases\n\t"
                   "a new-style class can't have only classic bases")
            raise TypeError(msg)


def get_exec_body(**kwargs):
    '''Return an `exec_body` function that update `ns` with `kwargs`.'''
    def exec_body(ns):
        ns.update(kwargs)
        return ns
    return exec_body
