#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Synchronization lock tools.

A lock object is a synchronization primitive.  Locks are used as Python
Context Managers with only one method (`enter`) and one property (`locked`).

The method `enter` is used with the Python ``with`` statement and the property
`locked` is logically True or False depending if the lock is active or not.

For example::

  >>> from xoutil.lock import context_lock as ctx

  >>> def get_lock_value():
  ...     return 'Yes' if ctx.locked else 'No'

  >>> with ctx.enter():
  ...     one = get_lock_value()
  >>> two = get_lock_value()
  >>> (one, two)
  ('Yes', 'No')


Locks are implemented using module-property; this means that each time you
import it, a different lock is returned::

  >>> from xoutil.tasking.lock import context_lock as one
  >>> from xoutil.tasking.lock import context_lock as two
  >>> one is two
  False

The function `context_lock`:func: implement a module property to create a
class that use an execution context, see `xoutil.context`:mod: module for more
information.

If other lock mechanisms are going to be implementing, for example using
threading, this is the place.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from xoutil.modules import moduleproperty


@moduleproperty
def context_lock(self):
    '''Allocate a lock based on Xoutil execution contexts.'''
    from xoutil.objects import classproperty

    class ContextLock:
        '''A class representing the lock.

        See `xoutil.lock`:mod: module for more information.

        '''
        def __new__(cls, *args, **kwargs):
            msg = '"{}" could not be instanced.'.format(cls.__name__)
            raise RuntimeError(msg)

        @classmethod
        def enter(cls, **kwargs):
            '''Enter the context.'''
            from xoutil.context import context
            return context(cls, **kwargs)

        @classproperty
        def locked(cls):
            from xoutil.context import context
            return context[cls]

    return ContextLock


del moduleproperty
