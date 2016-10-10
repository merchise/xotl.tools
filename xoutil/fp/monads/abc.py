#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.fp.monads.abc
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-10-01

'''Abstract Base Classes for monadic definitions.

.. See full xoutil documentation for more information about this module.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.eight.abc import ABC, abstractmethod


class Functor(ABC):
    '''Class for types which can be mapped over.

    It has a single method (`map`:meth:) represented by the infix operator
    ``%``.

    '''

    @abstractmethod
    def map(self, fn):
        '''Map a function over monadic enclosed values.

        Parameters are usually expressed as Haskell types.

        :param fn: ``a -> b``

        :returns: Mapped `Functor` instance.

        '''
        return NotImplemented

    def __rmod__(self, fn):
        '''Infix version of `map`.

        Example::

          >>> (lambda x: 2*x + 1) % Just(1)
          3

        '''
        return self.map(fn)

    @property
    def value(self):
        '''Inner value.

        Use the `map` method together with the identity function (``id``) to
        extract inner value.

        This is tricky because some functors could wrap several values instead
        only one, in that case a `ValueError` will be raised.

        You can extract all values using: ``id % functor``.

        '''
        aux = [0, None]    # [count, value]

        def inner(arg):
            aux[0] += 1    # count
            if aux[0] == 1:
                aux[1] = arg    # value
            else:
                raise ValueError('More than one value.')

        self.map(inner)

        count, value = aux
        if count:
            return value
        else:
            raise ValueError('No inner values.')


class Monoid(ABC):
    '''Data type which support *appending*.'''

    @classmethod
    @abstractmethod
    def empty(cls):
        '''Neutral element for the associative operation.'''
        return NotImplemented

    @abstractmethod
    def append(self, other):
        '''The associative operation.'''
        return NotImplemented

    def __add__(self, other):
        return self.append(other)

    @classmethod
    def concat(cls, xs):
        '''Fold a monoid list.

        :param xs: The list of `Monoid` instances.

        :returns: Resulting `Monoid` instance.

        This default definition could be used in most cases, but this method
        must be overridden in specific implementations if optimization
        considerations are in place.

        '''
        return reduce(lambda m1, m2: m1.append(m2), xs, cls.empty())


class Applicative(ABC):
    '''Applicative functors are functors with some extra properties.'''

    @classmethod
    def pure(cls, fn):
        '''Lifts any value inside the functor.

        The *Applicative Functor* constructor.

        :param fn: Function from a normal value to an `Aplicative` instance.

        '''
        return cls(fn)

    @abstractmethod
    def apply(self, target):
        '''Change a function in the functor to one over values of the functor.

        :param target: `Applicative`.

        :returns: `Applicative`.

        ``(<*>)`` is a beefed up ``fmap``.  It takes a functor value that has
        a function in it and another functor, and extracts that function from
        the first functor and then maps it over the second one.

        '''
        return NotImplemented

    def __mul__(self, target):
        '''Infix version (``*``) of `apply`.'''
        return self.apply(target)


class Monad(ABC):
    '''Generic template specifying a *sequence of operations*.'''

    @classmethod
    def unit(cls, value):
        '''Wrap a value in a default context.'''
        return cls(value)

    @abstractmethod
    def bind(self, fn):
        '''Central method that can be used for almost anything.'''
        return NotImplemented

    def __rshift__(self, fn):
        '''Infix version of `bind` (instead of the Haskell's ``>>=``).'''
        return self.bind(fn)

    def then(self, other):
        '''Version of  "then" (instead of the Haskell's ``>>``).

        Sequentially compose two monadic actions, discarding any value
        produced by the first, like sequencing operators (such as the
        semicolon) in imperative languages.

        It is a mere convenience and commonly implemented as::

          m >> n = m >>= \_ -> n

        '''
        return self.bind(lambda _: other)


class CategoricalMonad(Monad, Applicative, Monoid, Functor):
    '''A full monad base using *category theory* definition.

    `Monadic` can be used as an alias for this base class.

    '''

    def map(self, fn):
        '''Map a function over monadic enclosed values.'''
        from xoutil.fp.tools import compose
        return self.bind(compose(self.unit, fn))

    def join(self):
        '''Turns a container of containers into a single container.'''
        from xoutil.fp.tools import identity
        return self.bind(identity)


Monadic = CategoricalMonad
