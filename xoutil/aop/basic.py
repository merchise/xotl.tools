#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.aop.basic
#----------------------------------------------------------------------
# Copyright (c) 2012 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on Mar 23, 2012

'''
Very simple AOP implementation allowing method replacing in objects with change
function, reset an object to its original state and user a special super
function inner new functions used to inject the new behavior.

Aspect-oriented programming (AOP) increase modularity by allowing the separation
of cross-cutting concerns.

An aspect can alter the behavior of the base code (the non-aspect part of a
program) by applying advice (additional behavior) at various join-points (points
in a program) specified in a quantification or query called a point-cut (that
detects whether a given join point matches).

An aspect can also make structural changes to other classes, like adding members
or parents.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from types import MethodType, FunctionType
from contextlib import contextmanager

from xoutil.objects import xdir

__docstring_format__ = 'rst'
__author__ = 'Medardo Rodriguez'


def _update(attrs, *sources):
    '''
    Updates attrs from sources:

    - Every source with a __name__ that is not a class is updated into attrs.

    - For every source that is a class, it's public attributes and all methods
      are updated into attrs.
    '''
    attrs.update({f.__name__: f for f in sources
                  if not isinstance(f, type) and getattr(f, '__name__',
                                                         False)})
    attrs.update({name: getattr(a, 'im_func', a) for f in sources
                        if isinstance(f, type)
                    for name, a in xdir(f)
                        if not name.startswith('_') or
                            getattr(a, 'im_func', False)})
    return attrs



def complementor(*sources, **attrs):
    '''
    Returns a decorator to be applied to a class in order to add attributes \
    in a smart way:

    - if the attribute is a dictionary and exists in the decorated class, it's
      updated.

    - If a list, tuple or set, the new value is appended.

    - Methods declared in the class that are replaces are renamed to
      "_super_<name>", but the docstring and names are copied to their
      replacement.

    - All other values are replaced.

    The following code tests show each case:

        >>> def hacked_init(self, *args, **kw):
        ...    print('Hacked')
        ...    self._super___init__(*args, **kw)

        >>> @complementor(somedict={'a': 1, 'b': 2}, somelist=range(5, 10),
        ...               __init__=hacked_init)
        ... class Someclass(object):
        ...     somedict = {'a': 0}
        ...     somelist = range(5)
        ...
        ...     def __init__(self, d=None, l=None):
        ...         'My docstring'
        ...         if d:
        ...             self.somedict.update(d)
        ...         if l:
        ...             self.somelist.extend(l)


        # It's best to do comparison with dicts since key order may not be
        # preserved.
        >>> Someclass.somedict == {'a': 1, 'b': 2}
        True

        >>> Someclass.somelist
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        >>> instance = Someclass(d={'c': 12}, l=(10, ))
        Hacked

        >>> instance.somedict == {'a': 1, 'b': 2, 'c': 12}
        True

        >>> instance.somelist
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        >>> Someclass.__init__.__doc__
        'My docstring'

    If any positional arguments :param:`sources` are given then for each of
    them:

    - If it's not a class (an instance of `type`) and it has a `__name__`, it
      will be updated into :param:`attrs` and treated according to the rules
      before.

    - If it's a class all it's public non-method attributes are updated into
      `attrs`, and all it's methods (public or private) are updated as well.

    Notice the order in which this is done: class takes precedence over other
    kind of sources, and sources takes precedence over keyword arguments.
    '''
    def inner(cls):
        from collections import (Mapping, MutableMapping,
                                 MutableSequence as List,
                                 Set)
        from xoutil.types import Unset
        for attr, value in attrs.iteritems():
            assigned = attr in cls.__dict__
            if assigned:
                ok = isinstance
                current = getattr(cls, attr)
                if ok(value, Mapping) and ok(current, MutableMapping):
                    current.update(value)
                    value = Unset
                elif ok(value, List) and ok(current, List):
                    current.extend(value)
                    value = Unset
                elif ok(value, tuple) and ok(current, tuple):
                    value = current + value
                elif ok(value, Set) and ok(current, Set):
                    value = current | value
                elif ok(value, (FunctionType, MethodType)) and current:
                    setattr(cls, b'_super_%s' % attr, current)
            else:
                current = None
            if value is not Unset:
                if isinstance(value, MethodType):
                    value = value.im_func
                if current and not getattr(value, '__doc__', False):
                    from functools import update_wrapper
                    update_wrapper(value, current)
                setattr(cls, attr, value)
        return cls

    _update(attrs, *sources)
    return inner



def contextualized(context, *sources, **attrs):
    '''
    Another decorator very similar to :func:`complementor`, but this wraps
    every method injected inside the context provided by :param:`context`.

        >>> from xoutil.context import context
        >>> class FooBazer(object):
        ...    def inside(self):
        ...        if context['in-context']:
        ...            print('in-context')
        ...        else:
        ...            print('outside-context')

        >>> @contextualized(context('in-context'), FooBazer)
        ... class Foobar(object):
        ...    def outside(self):
        ...        print('not-context')

        >>> foo = Foobar()
        >>> foo.inside()
        in-context

        >>> foo.outside()
        not-context

    '''
    def wrap(method):
        def inner(self, *args, **kwargs):
            with context:
                if getattr(method, 'im_self', None):
                    return method(*args, **kwargs)
                else:
                    return method(self, *args, **kwargs)
        return inner

    _update(attrs, *sources)
    wrapped_attrs = {}
    for name, value in attrs.items():
        if isinstance(value, (FunctionType, MethodType)):
            wrapped_attrs[name] = wrap(value)
    return complementor(**wrapped_attrs)


def inject_dependencies(target, *sources, **attrs):
    'Injects/replaces the sources for the given target.'
    cls = target if isinstance(target, type) else target.__class__
    _merchise_extended = cls.__dict__.get('_merchise_extended',
                                          {'depth': 0}).copy()
    _merchise_extended['depth'] += 1
    attrs.update({b'__doc__': cls.__doc__, b'__module__': b'merchise.builtin',
                  '_merchise_extended': _merchise_extended})
    _update(attrs, *sources)
    extended_class = type(cls.__name__, (cls,), attrs)
    if not isinstance(target, type):
        try:
            target.__class__ = extended_class
        except:
            class wrapper(target.__class__):
                pass
            target = wrapper(target)
            target.__class__ = extended_class
        result = target
    else:
        result = extended_class
    return result


@contextmanager
def weaved(target, *sources, **attrs):
    '''
    Returns a context manager that weaves :param:`target` with all the
    :param:`sources` and the :param:`attrs` weaved into it. This
    method yields the weaved object into the context manager, so you have
    access to it. Upon exiting the context manager, the :param:`target` is
    reset to it's previous state (if possible).

    For example, in the following code::

        >>> class Test(object):
        ...    def f(self, n):
        ...        return n

        >>> test = Test()


    You may want to record each call to ``f`` on the ``test`` object::

        >>> def f(self, n):
        ...     print('Log this')
        ...     return super(_ec, self).f(n) # Notice the assignment to _ec

        >>> with weaved(test, f) as test:
        ...    _ec = test.__class__ # Needed
        ...    test.f(10)
        Log this
        10

    But once you leave the context, ``test`` will stop logging::

        >>> test.f(10)
        10

    You may nest several calls to this:

        >>> def f2(self, n):
        ...    print('Done it')
        ...    return super(_ec2, self).f(n)

        >>> with weaved(test, f) as test:
        ...    _ec = test.__class__
        ...    with weaved(test, f=f2) as test:
        ...        _ec2 = test.__class__
        ...        test.f(10)
        ...    test.f(12)
        Done it
        Log this
        10
        Log this
        12

        >>> test.f(10)
        10

    '''
    try:
        result = inject_dependencies(target, *sources, **attrs)
        yield result
    finally:
        if result is target:
            cls = target.__class__
            res = 0
            depth = 0
            while depth == 0 and cls.__dict__.get('_merchise_extended'):
                depth = cls.__dict__.get('_merchise_extended',
                                         {}).get('depth', 0)
                cls = cls.__base__
                res += 1
            if res > 0:
                target.__class__ = cls
