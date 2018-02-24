#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Implements the metaclass() function using the Py3k syntax.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from ._meta import Mixin    # noqa

from ._meta3 import metaclass
metaclass.__doc__ = '''Define the metaclass of a class.

    .. versionadded:: 1.7.0

    .. deprecated:: 2.0.0  Not needed in a world without Python 2.

    This function allows to define the metaclass of a class equally in Python
    2 and 3.

    Usage::

     >>> class Meta(type):
     ...   pass

     >>> class Foobar(metaclass(Meta)):
     ...   pass

     >>> class Spam(metaclass(Meta), dict):
     ...   pass

     >>> type(Spam) is Meta
     True

     >>> Spam.__bases__ == (dict, )
     True

    .. versionadded:: 1.5.5 The `kwargs` keywords arguments with support for
       ``__prepare__``.

    Metaclasses are allowed to have a ``__prepare__`` classmethod to return
    the namespace into which the body of the class should be evaluated.  See
    `3115`:pep:.

    .. seealso:: `xoutil.future.types.prepare_class`:func: and
       `xoutil.future.types.new_class`:func:.

    .. versionchanged:: 1.7.1 Now are accepted atypical meta-classes, for
       example functions or any callable with the same arguments as those that
       type accepts (class name, tuple of base classes, attributes mapping).

'''

metaclass.__module__ = __name__
