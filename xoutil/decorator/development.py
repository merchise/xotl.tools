#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

from xoutil.decorator.meta import decorator


# TODO: move to new module 'xoutil.hints' when fully implemented.

@decorator
def unstable(target, msg=None):
    '''Declares that a method, class or interface is unstable.

    This has the side-effect of issuing a warning the first time the `target`
    is invoked.

    The `msg` parameter, if given, should be string that contains, at most,
    two positional replacement fields ({0} and {1}). The first replacement
    field will be the type of `target` (interface, class or function) and the
    second matches `target's` full name.

    '''
    import warnings
    from xoutil.names import nameof
    from xoutil.eight import class_types
    if msg is None:
        msg = ('The {0} `{1}` is declared unstable. '
               'It may change in the future or be removed.')
    try:
        from zope.interface import Interface
    except ImportError:
        from xoutil.symbols import Ignored as Interface
    if isinstance(target, type(Interface)):
        objtype = 'interface'
    elif isinstance(target, class_types):
        objtype = 'class'
    else:
        objtype = 'function or method'
    message = msg.format(objtype,
                         nameof(target, inner=True, full=True))
    if isinstance(target, class_types) or issubclass(type(target),
                                                     type(Interface)):
        class meta(type(target)):
            pass

        def new(*args, **kwargs):
            warnings.warn(message, stacklevel=2)
            return target.__new__(*args, **kwargs)
        klass = meta(target.__name__, (target,), {'__new__': new})
        return klass
    else:
        def _unstable(*args, **kwargs):
            message = msg.format(objtype,
                                 nameof(target, inner=True, full=True))
            warnings.warn(message, stacklevel=2)
            return target(*args, **kwargs)
        return _unstable


del decorator
