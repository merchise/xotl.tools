#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Tools for managing function arguments.

Process function arguments could be messy when a flexible schema is needed.
With this module you can outline parameters schema using a smart way of
processing actual arguments:

A parameter row (see `ParamSchemeRow`:class:), allow several keywords IDs (one
is required used as the final identifier for the actual argument). Also
integer IDs expressing logical order for positional argument passing (negative
values are for right-to-left indexing, like in sequences).  Several values
means several possibilities.

.. versionadded:: 1.8.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)


#: The maximum number of positional arguments allowed when calling a function.
MAX_ARG_COUNT = 1024 * 1024    # just any large number

from xoutil.symbols import Undefined    # used implicitly for absent default


def issue_9137(args):
    '''Parse arguments for methods, fixing `issue 9137`__ (self ambiguity).

    There are methods that expect 'self' as valid keyword argument, this is
    not possible if this name is used explicitly::

        def update(self, *args, **kwds):
            ...

    To solve this, declare the arguments as ``method_name(*args, **kwds)``,
    and in the function code::

        self, args = issue_9137(args)

    :returns: (self, remainder positional arguments in a tuple)

    .. versionadded:: 1.8.0

    __ https://bugs.python.org/issue9137

    '''
    self = args[0]    # Issue 9137
    args = args[1:]
    return self, args


def check_count(args, low, high=MAX_ARG_COUNT, caller=None):
    '''Check the positional arguments actual count against constrains.

    :param args: The args to check count, normally is a tuple, but an integer
           is directly accepted.

    :param low: Integer expressing the minimum count allowed.

    :param high: Integer expressing the maximum count allowed.

    :param caller: Name of the function issuing the check, its value is used
           only for error reporting.

    .. versionadded:: 1.8.0


    '''
    from xoutil.eight import integer_types
    # TODO: Shouldn't we use the TypeError and ValueError?
    assert isinstance(low, integer_types) and low >= 0
    assert isinstance(high, integer_types) and high >= low
    if isinstance(args, int):
        count = args
        if count < 0:
            msg = "check_count() don't accept a negative argument count: {}"
            raise ValueError(msg.format(count))
    else:
        count = len(args)
    if count < low:
        error = True
        adv = 'exactly' if low == high else 'at least'
        if low == 1:
            aux = '{} one argument'.format(adv)
        else:
            aux = '{} {} arguments'.format(adv, low)
    elif count > high:
        error = True
        if low == high:
            if low == 0:
                aux = 'no arguments'
            elif low == 1:
                aux = 'exactly one argument'
            else:
                aux = 'exactly {} arguments'.format(low)
        elif high == 1:
            aux = 'at most one argument'
        else:
            aux = 'at most {} arguments'.format(high)
    else:
        error = False
    if error:
        if caller:
            name = '{}()'.format(caller)
        else:
            name = 'called function or method'
        raise TypeError('{} takes {} ({} given)'.format(name, aux, count))


def check_default(absent=Undefined):
    '''Get a default value passed as a last excess positional argument.

    :param absent: The value to be used by default if no one is given.
           Defaults to `~xoutil.symbols.Undefined`:obj:.

    For example::

        def get(self, name, *default):
            from xoutil.params import check_default, Undefined
            if name in self.inner_data:
                return self.inner_data[name]
            elif check_default()(*default) is not Undefined:
                return default[0]
            else:
                raise KeyError(name)

    .. versionadded:: 1.8.0

    '''
    def default(res=absent):
        return res
    return default


def single(args, kwds):
    '''Return a true value only when a unique argument is given.

    When needed, the most suitable result will be wrapped using the
    `~xoutil.fp.option.Maybe`:class:\ .

    .. versionadded:: 1.8.0

    '''
    from xoutil.fp.option import Just, Wrong, take
    if len(args) == 1 and not kwds:
        res = take(args[0])
        if not res:
            res = Just(res)
        res = Just(res)
    elif not args and len(kwds) == 1:
        res = kwds
    else:
        res = Wrong((args, kwds))
    return res


def keywords_only(func):
    '''Make a function to accepts its keywords arguments as keywords-only.

    In Python 3 parlance this would make::

       func(a, b=None)

    become::

       func(a, *, b=None).

    In Python 3 this decorator does nothing.  If `func` does not have any
    keyword arguments, return `func`.

    There's a pathological case when you define::

       func(a, b=None, *args)

    In such a case if you call ``func(1, 2, b=3)`` we can't actually call
    the original function with ``a=1``, ``args=(2, )`` and ``b=3``.  This
    case also raises a TypeError.

    .. versionadded:: 1.8.0

    '''
    import sys
    from functools import wraps
    from xoutil.future.inspect import getfullargspec
    if sys.version_info >= (3, 0):
        return func

    spec = getfullargspec(func)
    if not spec.defaults:
        return func

    l = len(spec.args) - len(spec.defaults)
    kargs = spec.args[l:]
    if len(kargs) > 1:
        display_kargs = ', '.join("'%s'" % arg for arg in spec.args[l:-1])
        display_kargs += " and '%s'" % spec.args[-1]
    else:
        display_kargs = "'%s'" % spec.args[l]

    InvalidSignature = TypeError(
        'Arguments %s must be passed as keyword' % (display_kargs, )
    )

    @wraps(func)
    def inner(*args, **kwargs):
        if len(args) > l:
            # The case of ``def f(a, b=X, *args)`` because if we call
            # ``f(1, 2, b=3)`` we cannot properly call the original
            # function with a=1, args=(2, ) and b=3.
            raise InvalidSignature
        return func(*args, **kwargs)

    return inner


def pop_keyword_arg(kwargs, names, default=Undefined):
    '''Return the value of a keyword argument.

    :param kwargs: The mapping with passed keyword arguments.

    :param names: Could be a single name, or a collection of names.

    :param default: The default value to return if no value is found.

    .. versionadded:: 1.8.0

    '''
    from xoutil.eight import string_types
    from xoutil.objects import pop_first_of
    if isinstance(names, string_types):
        names = (names,)
    return pop_first_of(kwargs, *names, default=default)


def pop_keyword_values(kwargs, *names, **options):
    '''Return a list with all keyword argument values.

    :param kwargs: The mapping with passed keyword arguments.

    :param names: Each item will be a definition of keyword argument name to
           retrieve.  Could be a string with a name, or a list of alternatives
           (aliases).

    :keyword default: Keyword only option to define a default value to be used
           in place of not given arguments.  If not given, it is used
           special value `~xoutil.symbols.Undefined`:obj:.

    :keyword defaults: A dictionary with default values per argument name. If
           none is given, use `default`.

           .. note:: `defaults` trumps `default`.

           .. warning:: For the case where a single name has several
              alternatives, you may choose any of the alternatives.  If you
              pass several diverging defaults for different alternatives, the
              result is undefined.

    :keyword ignore_error: By default, when there are remaining values in
           `kwargs`, after all names are processed, a `TypeError`:class: is
           raised.  If this keyword only option is True, this function returns
           normally.

    Examples::

      >>> pop_keyword_values({'b': 1}, 'a', 'b')
      [Undefined, 1]

      >>> kwargs = {'a': 1, 'b': 2, 'c': 3}
      >>> try:
      ...     res = pop_keyword_values(kwargs, 'a', 'b')
      ... except TypeError as error:
      ...     res = error
      >>> type(res)
      TypeError

      >>> kwargs = {'a': 1, 'b': 2, 'c': 3}
      >>> options = dict(ignore_error=True, default=None)
      >>> pop_keyword_values(kwargs, 'a', ('B', 'b'), **options)
      [1, 2]

    .. versionadded:: 1.8.3

    '''
    default = options.get('default', Undefined)
    defaults = options.get('defaults', {})
    res = []
    for item in names:
        val = pop_keyword_arg(kwargs, item, default=Undefined)
        if val is Undefined:
            val = pop_keyword_arg(defaults, item, default=default)
        res.append(val)
    if kwargs and not options.get('ignore_error', False):
        msg = 'calling function got unexpected keyword arguments "{}"'
        raise TypeError(msg.format(tuple(kwargs)))
    return res


class ParamManager(object):
    '''Function parameters parser.

    For example::

      def wraps(*args, **kwargs):
          pm = ParamManager(args, kwargs)
          name = pm(0, 1, 'name', coerce=str)
          wrapped = pm(0, 1, 'wrapped', coerce=valid(callable))
          ...

    When an instance of this class is called (``__call__`` operator), it is
    used the same protocol as when creating an instance of a parameter
    definition row (`ParamSchemeRow`:class:).

    See `ParamScheme`:class: class as another way to define and validate
    schemes for extracting parameter values in a consistent way.


    .. versionadded:: 1.8.0

    '''

    def __init__(self, args, kwds):
        '''Created with actual parameters of a client function.'''
        self.args = args
        self.kwds = kwds
        self.consumed = set()    # consumed identifiers

    def __call__(self, *ids, **options):
        '''Get a parameter value.'''
        from xoutil.fp.option import Just, Wrong, none
        # TODO: Change this ``from xoutil.values import coercer``
        from xoutil.fp.prove.semantic import predicate as coercer
        args, kwds = self.args, self.kwds
        i, res = 0, none
        while isinstance(res, Wrong) and i < len(ids):
            key = ids[i]
            if key in self.consumed:
                pass
            elif isinstance(key, int):
                try:
                    res = args[key]
                except IndexError:
                    pass
            elif key in kwds:
                res = kwds[key]
            if not isinstance(res, Wrong) and 'coerce' in options:
                aux = coercer(options['coerce'])(res)
                res = aux.inner if isinstance(aux, Just) else aux
            if not isinstance(res, Wrong):
                self.consumed.add(key)
                if isinstance(key, int) and key < 0:
                    # consume both, negative and adjusted value
                    key = len(args) + key
                    self.consumed.add(key)
            else:
                i += 1
        if isinstance(res, Wrong):
            if 'default' in options:
                return options['default']
            elif isinstance(res.inner, BaseException):
                from xoutil.eight.exceptions import throw
                throw(res.inner)
            else:
                raise TypeError('value for "{}" is not found'.format(ids))
        else:
            return res.inner if isinstance(res, Just) else res

    def remainder(self):
        '''Return not consumed values in a mapping.'''
        from xoutil.eight import range
        passed = set(range(len(self.args))) | set(self.kwds)
        ids = passed - self.consumed
        args, kwds = self.args, self.kwds
        return {k: args[k] if isinstance(k, int) else kwds[k] for k in ids}


class ParamSchemeRow(object):
    '''Scheme row for a  `ParamManager`:class: instance call.

    This class validates identifiers and options at this level; these
    checks are not done in a call to get a parameter value.

    Normally this class is used as part of a full `ParamScheme`:class:
    composition.

    Additionally to the options can be passed to
    `ParamManager.__call__`:meth:', this class can be instanced with:

    :param ids: positional variable number arguments, could be aliases for
           keyword parameter passing, or integers for order (negative values
           are means right-to-left indexing, like in sequences);

    :param key: an identifier to be used when the parameter is only positional
           or when none of the possible keyword aliases must be used as the
           primary-key;

    :param default: keyword argument, value used if the parameter is absent;

    :param coerce: check if a value is valid or not and convert to its
           definitive value; see `xoutil.values`:mod: module for more
           information.

    .. versionadded:: 1.8.0

    '''
    __slots__ = ('ids', 'options', '_key')

    def __init__(self, *ids, **options):
        from collections import Counter
        from xoutil.eight import iteritems, string_types as strs
        from xoutil.eight.string import safe_isidentifier as iskey
        from xoutil.eight import type_name
        from xoutil.fp.option import none
        # TODO: Change this ``from xoutil.values import coercer``
        from xoutil.fp.prove.semantic import predicate as coercer
        aux = {k: c for k, c in iteritems(Counter(ids)) if c > 1}
        if aux:
            parts = ['{!r} ({})'.format(k, aux[k]) for k in aux]
            msg = '{}() repeated identifiers: {}'
            raise TypeError(msg.format(type_name(self), ', '.join(parts)))
        else:
            def ok(k):
                return (isinstance(k, strs) and iskey(k) or
                        isinstance(k, int))

            bad = [k for k in ids if not ok(k)]
            if bad:
                msg = ('{}() identifiers with wrong type (only int and str '
                       'allowed): {}')
                raise TypeError(msg.format(type_name(self), bad))
        key = options.pop('key', none)
        if not (key is none or iskey(key)):
            msg = ('"key" option must be an identifier, "{}" of type "{}" '
                   'given')
            raise TypeError(msg.format(key), type_name(key))
        if 'default' in options:
            aux = {'default': options.pop('default')}
        else:
            aux = {}
        if 'coerce' in options:
            aux['coerce'] = coercer(options.pop('coerce'))
        if options:
            msg = '{}(): received invalid keyword parameters: {}'
            raise TypeError(msg.format(type_name(self), set(options)))
        self.ids = ids
        self.options = aux
        self._key = key

    def __str__(self):
        from xoutil.eight import iteritems
        parts = [repr(k) for k in self.ids]
        for key, value in iteritems(self.options):
            parts.append('{}={!r}'.format(key, value))
        aux = ', '.join(parts)
        return 'ParamSchemeRow({})'.format(aux)
    __repr__ = __str__

    def __call__(self, *args, **kwds):
        '''Execute a scheme-row using as argument a `ParamManager` instance.

        The concept of `ParamManager`:class: instance argument is a little
        tricky: when a variable number of arguments is used, if only one
        positional and is already an instance of `ParamManager`:class:, it is
        directly used; if two, the first is a `tuple` and the second is a
        `dict`, these are considered the constructor arguments of the new
        instance; otherwise all arguments are used to build the new instance.

        '''
        count = len(args)
        if count == 1 and not kwds and isinstance(args[0], ParamManager):
            manager = args[0]
        else:
            if count == 2 and not kwds:
                a, k = args
                if isinstance(a, tuple) and isinstance(k, dict):
                    args, kwds = a, k
            manager = ParamManager(args, kwds)
        return manager(*self.ids, **self.options)

    @property
    def default(self):
        '''Returned value if parameter value is absent.

        If not defined, special value ``none`` is returned.

        '''
        from xoutil.fp.option import none
        return self.options.get('default', none)

    @property
    def key(self):
        '''The primary key for this scheme-row definition.

        This concept is a little tricky (the first string identifier if some
        is given, if not then the first integer).  This definition is useful,
        for example, to return remainder not consumed values after a scheme
        process is completed (see `ParamManager.remainder`:meth: for more
        information).

        '''
        # TODO: calculate the key value in the constructor
        from xoutil.eight import string_types as strs
        from xoutil.fp.option import none
        res = self._key
        if res is none:
            res = next((k for k in self.ids if isinstance(k, strs)), None)
            if res is None:
                res = self.ids[0]
            self._key = res
        return res


class ParamScheme(object):
    '''Full scheme for a  `ParamManager`:class: instance call.

    This class receives a set of `ParamSchemeRow`:class: instances and
    validate them as a whole.

    .. versionadded:: 1.8.0

    '''
    __slots__ = ('rows', 'cache')

    def __init__(self, *rows):
        from xoutil.eight import string_types as strs, type_name
        from xoutil.params import check_count
        check_count(len(rows) + 1, 2, caller=type_name(self))
        used = set()
        for idx, row in enumerate(rows):
            if isinstance(row, ParamSchemeRow):
                this = {k for k in row.ids if isinstance(k, strs)}
                aux = used & this
                if not aux:
                    used |= this
                else:
                    msg = ('{}() repeated keyword identifiers "{}" in '
                           'row {}').format(type_name(self), aux, idx)
                    raise ValueError(msg)
        self.rows = rows
        self.cache = None

    def __str__(self):
        from xoutil.eight import type_name
        aux = ',\n\i'.join(str(row) for row in self)
        return '{}({})'.format(type_name(self), aux)

    def __repr__(self):
        from xoutil.eight import type_name
        return '{}({} rows)'.format(type_name(self), len(self))

    def __len__(self):
        '''The defined scheme-rows number.'''
        return len(self.rows)

    def __getitem__(self, idx):
        '''Obtain the scheme-row by a given index.'''
        from xoutil.eight import string_types
        if isinstance(idx, string_types):
            cache = self._getcache()
            return cache[idx]
        else:
            return self.rows[idx]

    def __iter__(self):
        '''Iterate over all defined scheme-rows.'''
        return iter(self.rows)

    def __call__(self, args, kwds, strict=True):
        '''Get a mapping with all resulting values.

        If special value 'none' is used as 'default' option in a scheme-row,
        corresponding value isn't returned in the mapping if the parameter
        value is missing.

        '''
        from xoutil.eight import type_name

        def ok(v):
            from xoutil.fp.option import Wrong
            return not isinstance(v, Wrong)

        pm = ParamManager(args, kwds)
        aux = ((row.key, row(pm)) for row in self)
        res = {key: value for key, value in aux if ok(value)}
        rem = pm.remainder()
        if strict:
            if rem:
                msg = ('after a full `{}` process, there are still remainder '
                       'parameters: {}')
                raise TypeError(msg.format(type_name(self), set(rem)))
        else:
            res.update(rem)
        return res

    def keys(self):
        '''Partial compatibility with mappings.'''
        from xoutil.eight import iterkeys
        return iterkeys(self._getcache())

    def items(self):
        '''Partial compatibility with mappings.'''
        from xoutil.eight import iteritems
        return iteritems(self._getcache())

    @property
    def defaults(self):
        '''Return a mapping with all valid default values.'''
        def ok(v):
            from xoutil.fp.option import Wrong
            return not isinstance(v, Wrong)

        aux = ((row.key, row.default) for row in self)
        return {k: d for k, d in aux if ok(d)}

    def _getcache(self):
        if not self.cache:
            self.cache = {row.key: row for row in self}
        return self.cache
