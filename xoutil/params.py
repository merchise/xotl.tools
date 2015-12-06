#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.values
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created 2015-07-13

'''Basic function argument manager.

This module must avoid dependencies on modules that aren't basic enough that
could be the use of this one itself.

A `Coercer`:class: is a concept that combine two elements: validity check and
value moulding.  Most times only the first part is needed because the original
value is in the correct shape if valid.

It's usual to declare functions or methods with generic prototypes::

  def func(*args, **kwargs):
      ...

Actual parameters must be identified in a smart way.  This module provide a
tool to solve argument identification from scheme definition::

  scheme, row = ParamScheme, ParamSchemeRow
  sample_scheme = scheme(
      row('stream', 0, -1, 'output', default=sys.stdout, coerce=file_coerce),
      row('indent', 0, 1, default=1, coerce=positive_int),
      row('width', 0, 1, 2, 'max_width', default=79, coerce=positive_int),
      row('newline', default='\n', coerce=string_types))

A scheme-row can be used in an independent way using a `ParamManager`:class:
instance.

.. versionadded:: 1.7.0

.. versionchanged:: 1.7.2 Migrated to a completely new shape forgetting
       initially created `ParamConformer` class.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


class BooleanWrapper(object):
    '''A wrapper for valid results.'''
    __slots__ = 'inner'

    def __new__(cls, *args):
        default = cls is Right
        if len(args) == 0:
            arg = default
        elif len(args) == 1:
            arg = args[0]
        else:
            msg = '{}: receive too many arguments "{}"'
            raise TypeError(msg.format(cls.__name__, len(args)))
        if arg is default:
            if cls._singleton is None:
                self = super(BooleanWrapper, cls).__new__(cls)
                self.inner = arg
                cls._singleton = self
            return cls._singleton
        elif cls is BooleanWrapper:
            return (Right if arg else Wrong)(arg)
        elif isinstance(arg, cls):
            return arg
        elif not isinstance(arg, BooleanWrapper):
            self = super(BooleanWrapper, cls).__new__(cls)
            self.inner = arg
            return self
        else:
            msg = 're-wrapping inverted value: {}({})'
            raise ValueError(msg.format(cls.__name__, arg))

    def __init__(self, *args):
        pass

    def __nonzero__(self):
        return isinstance(self, Right)
    __bool__ = __nonzero__

    def __str__(self):
        return '{}({!r})'.format(type(self).__name__, self.inner)
    __repr__ = __str__

    def __eq__(self, other):
        return (isinstance(other, type(self)) and self.inner == other.inner or
                self.inner is other)    # TODO: check if `==` instead `is`

    def __ne__(self, other):
        return not (self == other)


class Right(BooleanWrapper):
    '''A wrapper for valid results.'''
    __slots__ = ()
    _singleton = None


class Wrong(BooleanWrapper):
    '''A wrapper for invalid results.'''
    __slots__ = ()
    _singleton = None

    def __new__(cls, *args):
        self = super(Wrong, cls).__new__(cls, *args)
        if isinstance(self.inner, BaseException):
            from xoutil.eight.exceptions import with_traceback
            from sys import exc_info
            info = exc_info()
            if info[1] is self.inner:
                self.inner = with_traceback(self.inner, info[2])
        return self

_false, _true = Wrong(), Right()


def _tname(arg):
    'Return the type name.'
    from xoutil.eight import typeof
    return typeof(arg).__name__


def _nameof(arg):
    'Obtain a nice name in a safe way.'
    try:
        res = arg.__name__
        _lambda_name = (lambda x: x).__name__
        return 'λ' if res == _lambda_name else res
    except AttributeError:
        if isinstance(arg, Coercer):
            return str(arg)
        else:
            return '{}(…)'.format(_tname(arg))


class Coercer(object):
    '''Wrapper for value-coercing definitions.

    A coercer combine check for validity and value mould (casting).  Could be
    defined from a type (or tuple of types), a callable or a list containing
    two parts with both concepts.

    To signal that value as invalid, a coercer must return the special value
    `_wrong`.  Types work as in `isinstance`:func: standard function; callable
    functions mould a parameter value into a definitive form.

    To use normal functions as a callable coercer, use `SafeCheck`:class: or
    `LogicalCheck`:class` to wrap them.

    When using a list to combine explicitly the two concepts, result of the
    check part is considered Boolean (True or False), and the second part
    alwasy return a moulded value.

    When use a coercer, several definitions will be tried until one succeed.

    '''
    __slots__ = ('inner',)

    def __new__(cls, *args):
        from xoutil.eight import class_types, callable
        if cls is Coercer:    # Parse the right sub-type
            _type_def = class_types + (tuple,)
            if len(args) == 0:
                msg = 'a {} takes at least 1 argument (0 given)'
                raise TypeError(cls.__name__, msg)
            elif len(args) == 1:
                arg = args[0]
                if isinstance(arg, cls):
                    return arg
                elif isinstance(arg, _type_def):
                    return TypeCheck(arg)
                elif isinstance(arg, list):
                    return CheckAndCast(*arg)
                elif callable(arg):
                    return LogicalCheck(arg)
                else:
                    msg = '''can't parse a {} definition of type: "{}"'''
                    raise TypeError(msg.format(cls.__name__, _tname(arg)))
            else:
                return MultiCheck(*args)
        else:
            return super(Coercer, cls).__new__(cls)

    def __init__(self, *args):
        pass

    def __repr__(self):
        return str(self)


class TypeCheck(Coercer):
    '''Check if value is instance of given types.'''
    __slots__ = ()

    def __new__(cls, *args):
        from xoutil.eight import class_types as _types
        if args:
            if len(args) == 1 and isinstance(args[0], tuple):
                args = args[0]
            if all(isinstance(arg, _types) for arg in args):
                self = super(TypeCheck, cls).__new__(cls)
                self.inner = args
                return self
            else:
                wrong = (arg for arg in args if not isinstance(arg, _types))
                wnames = ', or '.join(_tname(w) for w in wrong)
                msg = '`TypeChecker` allows only valid types, not: ({})'
                raise TypeError(msg.format(wnames))
        else:
            msg = '{}() takes at least 1 argument (0 given)'
            raise TypeError(_tname(self), msg)

    def __call__(self, value):
        ok = isinstance(value, self.inner)
        return (value if value else Right(value)) if ok else Wrong(value)

    def __str__(self):
        aux = ', '.join(t.__name__ for t in self.inner)
        return 'instance-of({})'.format(aux)


class NoneOrTypeCheck(TypeCheck):
    '''Check if value is None or instance of given types.'''
    __slots__ = ()

    def __call__(self, value):
        if value is None:
            _types = self.inner
            i, res = 0, None
            while res is None and i < len(_types):
                try:
                    res = _types[i]()
                except BaseException:
                    pass
                i += 1
            return res if res is not None else Wrong(None)
        else:
            return super(NoneOrTypeCheck, self).__call__(value)

    def __str__(self):
        aux = super(NoneOrTypeCheck, self).__str__()
        return 'none-or-{}'.format(aux)


class TypeCast(TypeCheck):
    '''Cast a value to a correct type.'''
    __slots__ = ()

    def __call__(self, value):
        res = super(TypeCast, self).__call__(value)
        if not res:
            _types = self.inner
            i = 0
            while not res and i < len(_types):
                try:
                    res = _types[i](value)
                    if not res:
                        res = Right(res)
                except BaseException:
                    pass
                i += 1
        return res

    def __str__(self):
        aux = super(NoneOrTypeCheck, self).__str__()
        return 'none-or-{}'.format(aux)


class CheckAndCast(Coercer):
    '''Check if value, if valid cast it.

    Result value must be valid also.
    '''
    __slots__ = ()

    def __new__(cls, check, cast):
        from xoutil.eight import callable
        check = Coercer(check)
        if callable(cast):
            self = super(CheckAndCast, cls).__new__(cls)
            self.inner = (check, SafeCheck(cast))
            return self
        else:
            msg = '{}() expects a callable for cast, "{}" given'
            raise TypeError(msg.format(_tname(self), _tname(cast)))

    def __call__(self, value):
        check, cast = self.inner
        aux = check(value)
        if aux:
            res = cast(value)
            if check(res):
                return res
        else:
            res = aux
        if isinstance(res, Wrong):
            return res
        else:
            return Wrong(value)

    def __str__(self):
        check, cast = self.inner
        fmt = '({}(…) if {}(…) else _wrong)'
        return fmt.format(_nameof(cast), check)


class FunctionalCheck(Coercer):
    '''Check if value is valid with a callable function.'''
    __slots__ = ()

    def __new__(cls, check):
        from xoutil.eight import callable
        if isinstance(check, Coercer):
            return check
        elif callable(check):
            self = super(FunctionalCheck, cls).__new__(cls)
            self.inner = check
            return self
        else:
            msg = 'a functional check expects a callable but "{}" is given'
            raise TypeError(msg.format(_tname(check)))

    def __str__(self):
        suffix = 'check'
        kind = _tname(self).lower()
        if kind.endswith(suffix):
            kind = kind[:-len(suffix)]
        inner = _nameof(self.inner)
        return '{}({})()'.format(kind, inner)


class LogicalCheck(FunctionalCheck):
    '''Check if value is valid with a callable function.'''
    __slots__ = ()

    def __call__(self, value):
        try:
            res = self.inner(value)
            if res:
                if isinstance(res, Right):
                    return res
                elif res is True:
                    return Right(value)
                else:
                    return res
            elif isinstance(res, Wrong):
                return res
            elif res is False or res is None:    # XXX: None?
                return Wrong(value)
            else:
                return Wrong(res)
        except BaseException as error:
            return Wrong(error)


class SafeCheck(FunctionalCheck):
    '''Return a wrong value only if function produce an exception.'''
    __slots__ = ()

    def __call__(self, value):
        try:
            return self.inner(value)
        except BaseException as error:
            return Wrong(error)


class MultiCheck(Coercer):
    '''Return a wrong value only when all inner coercers fails.'''
    __slots__ = ()

    def __new__(cls, *args):
        inner = tuple(Coercer(arg) for arg in args)
        self = super(MultiCheck, cls).__new__(cls)
        self.inner = inner
        return self

    def __call__(self, value):
        coercers = self.inner
        i, res = 0, _false
        while isinstance(res, Wrong) and i < len(coercers):
            res = coercers[i](value)
            i += 1
        return res.inner if isinstance(res, Right) and res.inner else res

    def __str__(self):
        aux = ' OR '.join(str(c) for c in self.inner)
        return 'combo({})'.format(aux)


class ParamManager(object):
    '''Function parameter handler.

    For example::

      def wraps(*args, **kwargs):
          pm = ParamManager(args, kwargs)
          name = pm(0, 1, 'name', coerce=str)
          wrapped = pm(0, 1, 'wrapped', coerce=valid(callable))
          ...

    See `ParamSchemeRow`:class: and `ParamScheme`:class: classes to
    pre-define and validate schemes for extracting parameter values in a
    consistent way.

    '''

    def __init__(self, args, kwds):
        '''Created with actual parameters of a client function.'''
        self.args = args
        self.kwds = kwds
        self.consumed = set()    # consumed identifiers

    def __call__(self, *ids, **options):
        '''Get a parameter value.

        :param ids: parameter identifiers.

        :param options: keyword argument options.

        Options could be:

        - 'default': value used if the parameter is absent;

        - 'coerce': check if a value is valid or not and convert to its
          definitive value; see `coercer`:class: for more information.

        '''
        args, kwds = self.args, self.kwds
        i, res = 0, _false
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
                aux = Coercer(options['coerce'])(res)
                res = aux.inner if isinstance(aux, Right) else aux
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
            return res.inner if isinstance(res, Right) else res

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

    - 'key': an identifier to be used when the parameter is only positional or
      when none of the possible keyword aliases must be used as the
      primary-key.

    '''
    __slots__ = ('ids', 'options', '_key')

    def __init__(self, *ids, **options):
        from collections import Counter
        from xoutil.eight import iteritems, string_types as strs
        from xoutil.eight.string import safe_isidentifier as iskey
        aux = {k: c for k, c in iteritems(Counter(ids)) if c > 1}
        if aux:
            parts = ['{!r} ({})'.format(k, aux[k]) for k in aux]
            msg = '{}() repeated identifiers: {}'
            raise TypeError(msg.format(_tname(self), ', '.join(parts)))
        else:
            ok = lambda k: (isinstance(k, int) or
                            isinstance(k, strs) and iskey(k))
            bad = [k for k in ids if not ok(k)]
            if bad:
                msg = ('{}() identifiers with wrong type (only int and str '
                       'allowed): {}')
                raise TypeError(msg.format(_tname(self), bad))
        key = options.pop('key', _false)
        if not (key is _false or iskey(key)):
            msg = ('"key" option must be an identifier, "{}" of type "{}" '
                   'given')
            raise TypeError(msg.format(key), _tname(key))
        coerce = options.pop('coerce', _false)
        if 'default' in options:
            aux = {'default': options.pop('default')}
        else:
            aux = {}
        if coerce is not _false:
            aux['coerce'] = coerce
        if options:
            msg = '{}(): received invalid keyword parameters: {}'
            raise TypeError(msg.format(_tname(self), set(options)))
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

    def __call__(self, manager):
        if isinstance(manager, ParamManager):
            return manager(*self.ids, **self.options)
        else:
            msg = '{}() expects a `ParamManager` instance, "{}" given'
            raise TypeError(msg.format(_tname(self), _tname(manager)))

    @property
    def default(self):
        '''Returned value if parameter value is absent.

        If not defined, special value `_false` is returned.

        '''
        return self.options.get('default', _false)

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
        res = self._key
        if res is _false:
            res = next((k for k in self.ids if isinstance(k, strs)), None)
            if res is None:
                res = self.ids[0]
            self._key = res
        return res


class ParamScheme(object):
    '''Full scheme for a  `ParamManager`:class: instance call.

    This class receives a set of `ParamSchemeRow`:class: instances and
    validate them as a whole.

    '''
    __slots__ = ('rows', 'cache')

    def __init__(self, *rows):
        from xoutil.eight import string_types as strs
        if rows:
            used = set()
            for idx, row in enumerate(rows):
                if isinstance(row, ParamSchemeRow):
                    this = {k for k in row.ids if isinstance(k, strs)}
                    aux = used & this
                    if not aux:
                        used |= this
                    else:
                        msg = ('{}() repeated keyword identifiers "{}" in '
                               'row {}')
                        raise ValueError(msg.format(_tname(self), aux, idx))
            self.rows = rows
            self.cache = None
        else:
            msg = '{}() takes at least 1 argument (0 given)'
            raise TypeError(msg.format(_tname(self)))

    def __str__(self):
        aux = ',\n\i'.join(str(row) for row in self)
        return '{}({})'.format(_tname(self), aux)

    def __repr__(self):
        return '{}({} rows)'.format(_tname(self), len(self))

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

    def __call__(self, args, kwds, strict=False):
        '''Get a mapping with all resulting values.

        If special value '_false' is used as 'default' option in a scheme-row,
        corresponding value isn't returned in the mapping if the parameter
        value is missing.

        '''
        pm = ParamManager(args, kwds)
        aux = ((row.key, row(pm)) for row in self)
        res = {key: value for key, value in aux if value is not _false}
        aux = pm.remainder()
        if strict:
            if aux:
                msg = ('after a full `{}` process, there are still remainder '
                       'parameters: {}')
                raise TypeError(msg.format(_tname(self), set(aux)))
        else:
            res.update(aux)
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
        aux = ((row.key, row.default) for row in self)
        return {k: d for k, d in aux if d is not _false}

    def _getcache(self):
        if not self.cache:
            self.cache = {row.key: row for row in self}
        return self.cache


if __name__ == '__main__':
    print('Testing module `xoutil.params`')

    import sys
    from xoutil.eight import string_types
    from xoutil.cl import (file_coerce as cfile,
                           positive_int_coerce as cposint)

    scheme, row = ParamScheme, ParamSchemeRow

    sample_scheme = scheme(
        row('stream', 0, -1, 'output', default=sys.stdout, coerce=cfile),
        row('indent', 0, 1, default=1, coerce=cposint),
        row('width', 0, 1, 2, 'max_width', default=79, coerce=cposint),
        row('newline', default='\n', coerce=string_types))

    def test(*args, **kwargs):
        print('-'*80)
        print(">>>", args, "--", kwargs)
        try:
            print('...', sample_scheme.get(args, kwargs))
        except BaseException as error:
            print("???", '{}:'.format(type(error).__name__), error)

    test(4, 80)
    test(2, '80')
    test(4)
    test(80, indent=4, extra="I'm OK!")
    test(width=80)
    test(sys.stderr, 4, 80)
    test(4, sys.stderr, newline='\n\r')
    test(sys.stderr, 4, output=sys.stderr)
    test(sys.stderr, 4, 80, output=sys.stderr)
    test(4, -79)
