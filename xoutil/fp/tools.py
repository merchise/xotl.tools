#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Tools for working with functions in a more "pure" way.

'''

from xoutil.eight.abc import ABCMeta


def identity(arg):
    '''Returns its argument unaltered.'''
    return arg


def fst(pair, strict=True):
    '''Return the first element of `pair`.

    If `strict` is True, `pair` needs to unpack to exactly two values.  If
    `strict` is False this is the same as ``pair[0]``.

    .. note:: This is an idiomatic function intended for using in compositions
       or as the argument or high-level functions.  Don't use it in your code
       as a replacement of ``x[0]``.

    .. versionadded:: 1.8.5

    '''
    if strict:
        res, _ = pair
        return res
    else:
        return pair[0]


def snd(pair, strict=True):
    '''Return the second element of `pair`.

    If `strict` is True, `pair` needs to unpack to exactly two values.  If
    `strict` is False this is the same as ``pair[1]``.

    .. note:: This is an idiomatic function intended for using in compositions
       or as the argument or high-level functions.  Don't use it in your code
       as a replacement of ``x[1]``.

    .. versionadded:: 1.8.5

    '''
    if strict:
        _, res = pair
        return res
    else:
        return pair[1]


class MetaCompose(ABCMeta):

    '''Meta-class for function composition.'''
    def __instancecheck__(self, instance):
        '''Override for ``isinstance(instance, self)``.'''
        from xoutil.eight import callable
        res = super().__instancecheck__(instance)
        if not res:
            # TODO: maybe only those with parameters.
            res = callable(instance)
        return res

    def __subclasscheck__(self, subclass):
        '''Override for ``issubclass(subclass, self)``.'''
        res = super().__subclasscheck__(subclass)
        if not res:
            from xoutil.future.types import FuncTypes
            res = subclass in FuncTypes
        return res


class compose(metaclass=MetaCompose):
    '''Composition of several functions.

    Functions are composed right to left.  A composition of zero functions
    gives back the `identity`:func: function.

    The following rules (the arguments of `all`) are always true::

      >>> x = 15
      >>> f, g, h = x.__add__, x.__mul__, x.__xor__
      >>> all((compose() is identity,
      ...
      ...      # identity functions are optimized
      ...      compose(identity, f, identity) is f,
      ...
      ...      compose(f) is f,
      ...      compose(g, f)(x) == g(f(x)),
      ...      compose(h, g, f)(x) == h(g(f(x)))))
      True

    If any "intermediate" function returns an instance of:

    - `pos_args`:class:\ : it's expanded as variable positional arguments to
      the next function.

    - `kw_args`:class:\ : it's expanded as variable keyword arguments to the
      next function.

    - `full_args`:class:\ : it's expanded as variable positional and keyword
      arguments to the next function.

    The expected usage of these is **not** to have function return those types
    directly, but to use them when composing functions that return tuples and
    expect tuples.

    '''
    # TODO: __slots__ = ('inner', 'scope')

    def __new__(cls, *functions):
        functions = [fn for fn in functions if fn is not identity]
        count = len(functions)
        if count == 0:
            return identity
        else:
            from xoutil.eight import callable
            if all(callable(f) for f in functions):
                if count == 1:
                    return functions[0]
                else:
                    from xoutil.symbols import Unset
                    self = super().__new__(cls)
                    self.inner = functions
                    self.scope = Unset
                    return self
            else:
                raise TypeError('at least one argument is not callable')

    def __call__(self, *args, **kwds):
        funcs = self.inner
        count = len(funcs)
        if count:
            i = 1
            res = full_args((args, kwds))
            while i <= count:
                try:
                    fn = funcs[-i]
                    if isinstance(res, pos_args):
                        res = fn(*res)
                    elif isinstance(res, kw_args):
                        res = fn(**res)
                    elif isinstance(res, full_args):
                        res = fn(*res[0], **res[1])
                    else:
                        res = fn(res)
                except Exception:
                    # TODO: @med What's the point of of resetting scope under
                    # exception?  Should this `try..` even be?
                    self.scope = (count - i, fn)
                    raise
                i += 1
            return res
        else:
            return identity(*args, **kwds)

    def __repr__(self):
        '''Get composed function representation'''
        from xoutil.tools import nameof
        if self.inner:
            def getname(fn):
                return nameof(fn).replace((lambda: None).__name__, 'λ')
            return ' . '.join(getname(fn) for fn in self.inner)
        else:
            return nameof(identity)

    def __str__(self):
        '''Get composed function string'''
        count = len(self.inner)
        if count == 0:
            return identity.__doc__
        else:
            res = self.inner[0].__doc__ if count == 1 else None
            if not res:
                res = 'Composed function: <{!r}>'.format(self)
            return res

    def _get_name(self):
        res = self.__dict__.get('__name__')
        if res is None:
            res = repr(self)
        return res

    def _set_name(self, value):
        self.__dict__['__name__'] = value

    __name__ = property(_get_name, _set_name)

    def _get_doc(self):
        res = self.__dict__.get('__doc__')
        if res is None:
            res = str(self)
        return res

    def _set_doc(self, value):
        self.__dict__['__doc__'] = value

    __doc__ = property(_get_doc, _set_doc)

    def __eq__(self, other):
        if isinstance(type(other), MetaCompose):
            return self.inner == other.inner
        elif self.inner:
            return self.inner[0] == other
        else:
            return other is identity

    def __len__(self):
        return len(self.inner)

    def __iter__(self):
        return iter(self.inner)

    def __contains__(self, item):
        return item in self.inner

    def __getitem__(self, index):
        res = self.inner[index]
        return compose(*res) if isinstance(res, list) else res

    # TODO: Should we really allow compose be mutable?
    def __setitem__(self, index, value):
        if isinstance(index, slice) and isinstance(type(value), MetaCompose):
            value = value.inner
        self.inner[index] = value

    def __delitem__(self, index):
        del self.inner[index]


class pos_args(tuple):
    '''Mark variable number positional arguments (see `full_args`:class:).'''


class kw_args(dict):
    '''Mark variable number keyword arguments (see `full_args`:class:).'''


class full_args(tuple):
    '''Mark variable number arguments for composition.

    Pair containing positional and keyword ``(args, kwds)`` arguments.

    In standard functional composition, the result of a function is considered
    a single value to be use as the next function argument.  You can override
    this behaviour returning one instance of `pos_args`:class:,
    `kw_args`:class:, or this class; in order to provide multiple arguments to
    the next call.

    Since types are callable, you may use it directly in `compose`:func:
    instead of changing your functions to returns the instance of one of these
    classes::

      >>> def join_args(*args):
      ...     return ' -- '.join(str(arg) for arg in args)

      >>> compose(join_args, pos_args, list, range)(2)
      '0 -- 1'

      # Without 'pos_args', it prints the list
      >>> compose(join_args, list, range)(2)
      '[0, 1]'

    '''
    @staticmethod
    def parse(arg):
        '''Parse possible alternatives.

        If ``arg`` is:

        - a pair of a ``tuple`` and a ``dict``, return a `full_args`:class:
          instance.

        - a ``tuple`` or a ``list``, return a `pos_args`:class: instance;

        - a ``dict``, return a `kw_args`:class: instance;

        - ``None``, return an empty `pos_args`:class: instance.

        For example (remember that functions return 'None' when no explicit
        'return' is issued)::

          >>> def join_args(*args):
          ...     if args:
          ...         return ' -- '.join(str(arg) for arg in args)

          >>> compose(join_args, full_args.parse, join_args)()
          None

          # Without 'full_args.parse', return 'str(None)'
          >>> compose(join_args, join_args)()
          'None'

        '''
        if isinstance(arg, tuple):
            def check(pos, kw):
                return isinstance(pos, tuple) and isinstance(kw, dict)
            if len(arg) == 2 and check(*arg):
                return full_args(arg)
            else:
                return pos_args(arg)
        elif isinstance(arg, list):
            return pos_args(arg)
        elif isinstance(arg, dict):
            return kw_args(arg)
        elif arg is None:
            return pos_args()
        else:
            from xoutil.eight import typeof
            msg = 'Expecting None, a tuple, a list, or a dict; {} found'
            raise TypeError(msg.format(typeof(arg).__name__))
