# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.params
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created 2015-07-13


r'''Conformer for function parameter passing.

It's usual to declare functions with generic prototypes::

  def func(*args, **kwargs):
      ...

Actual parameters must be identified in a smart way.  This module provide a
tool to solve argument identification from a definition in a dictionary::

  {
    'main-name': (checker, pos-definition, aliases, default-value),
    ...
  }


- checker: A function that must validate a value; if valid return the same or
  a coerced value; if invalid must return the special value `Invalid`.  If not
  given, identity function is used (check as valid all values, avoid this).

- pos-definition: Define if the parameter could appear as a positional
  argument or not.  Must be a set of positive integers defining priority
  orders, parameters with minor values must appear first.  More than value
  means several alternatives.

  If not given, means that the parameter could not appear in positional
  arguments.

- aliases: A set of strings (valid Python identifiers), alternatives that
  could be used as keyword names.

- default: The default value to use if the argument is not given. The special
  value `Undefined` is used to specify that the parameter is required.

The value with each definition could miss several elements, each concept is
identified by its type, but ambiguities must be avoided; if default value is
confusing with some concept, must be the last one.

For example::

  scheme = {
      'stream': (check_file_like, {0, 3}, {'output'}, sys.stdout),
      'indent': (check_positive_int, {1}, 1),
      'width': (check_positive_int, {2}, {'max_width'}, 79),
      'newline': (check_str, '\n'),
  }

.. versionadded:: 1.7.0

'''


# TODO: Make a decorator to annotate function from a scheme.  See
# `xoutil.annotate`:mod: for more information.

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)


from xoutil.values import coercer


def _prepare_schema_coercer_global_cache():
    '''Prepare global cache for scheme coercer.'''
    from xoutil import Undefined
    from xoutil.eight import zip
    from xoutil.values import (coercer as checker_coerce,
                               iterable,
                               identity_coerce, identifier_coerce,
                               positive_int_coerce)
    pos_coerce = iterable(positive_int_coerce, outer_coerce=set)
    alias_coerce = iterable(identifier_coerce, outer_coerce=set)
    default_coerce = identity_coerce
    checker_default = identity_coerce
    pos_default = set()
    alias_default = set()
    default_default = Undefined
    names = ('checker', 'pos', 'aliases', 'default')
    coercers = dict(zip(names, (checker_coerce, pos_coerce, alias_coerce,
                                default_coerce)))
    defaults = dict(zip(names, (checker_default, pos_default, alias_default,
                                default_default)))
    return (names, coercers, defaults)


_SCHEME_COERCER_CACHE = _prepare_schema_coercer_global_cache()


@coercer
def scheme_coerce(arg):
    '''Coerce a scheme definition into a precise formalized dictionary.'''
    from xoutil.values import valid, Invalid
    names, coercers, defaults = _SCHEME_COERCER_CACHE
    if arg is Invalid:
        res = arg
    elif isinstance(arg, dict):
        res = arg
        i = 0
        keys = tuple(res)
        while valid(res) and i < len(keys):
            concept = keys[i]
            if concept in coercers:
                coercer = coercers[concept]
                value = coercer(res[concept])
                if valid(value):
                    res[concept] = value
                    i += 1
                else:
                    res = Invalid
            else:
                res = Invalid
    else:
        if not isinstance(arg, tuple):
            arg = (arg,)
        res = {}
        i = 0
        while valid(res) and i < len(arg):
            value = arg[i]
            j, found = 0, False
            while j < len(names) and not found:
                concept = names[j]
                if concept not in res:
                    coercer = coercers[concept]
                    v = coercer(value)
                    if valid(v):
                        found = True
                        res[concept] = v
                j += 1
            if found:
                i += 1
            else:
                res = Invalid
    if valid(res):
        # Complete and check default value
        for concept in defaults:
            if concept not in res:
                res[concept] = defaults[concept]
        concept = 'default'
        default = res[concept]
        if default is not defaults[concept]:
            coercer = res['checker']
            value = coercer(default)
            if valid(value):
                res[concept] = value
            else:
                res = Invalid
    return res


del coercer


class ParamConformer(object):
    '''Standardize actual parameters using a scheme.'''
    __slots__ = ('scheme', 'positions', 'strict')

    def __init__(self, *schemes, **kwargs):
        '''Create the conformer.

        :param schemes: Each item must be a dictionary with a scheme portion.
               See the module documentation for more information.

        :param kwargs: Except by the below special keyword argument, represent
               additional scheme definition, each keyword argument will
               represent the schema of a parameter with the same name.

        :param __strict__: Special keyword argument; if True, only scheme
               definitions could be used as actual arguments.

        '''
        self.strict = kwargs.pop('__strict__', False)
        self._formalize_schemes(schemes, kwargs)
        self._normalize_positions()

    def _formalize_schemes(self, schemes, kwargs):
        '''Formalize scheme in a more precise internal dictionary.'''
        from itertools import chain
        from xoutil.values import identifier_coerce, check as ok
        self.scheme = {}
        for scheme in chain((kwargs,), reversed(schemes)):
            for par in scheme:
                par = ok(identifier_coerce, par)
                if par not in self.scheme:
                    self.scheme[par] = ok(scheme_coerce, scheme[par])
        if self.scheme:
            self._check_duplicate_aliases()
        else:
            raise TypeError('Invalid empty scheme definition!')

    def _check_duplicate_aliases(self):
        '''Check if there are duplicate aliases and parameter names.'''
        from xoutil.eight import iteritems
        used = set(self.scheme)
        duplicated = set()
        for par, ps in iteritems(self.scheme):
            for alias in ps['aliases']:
                if alias in used:
                    duplicated.add(alias)
                else:
                    used.add(alias)
        if duplicated:
            msg = 'Duplicate identifiers detected: "{}"'
            raise TypeError(msg.format(', '.join(duplicated)))

    def _normalize_positions(self):
        '''Update the `positions` dictionaries.'''
        from xoutil.eight import range, iteritems
        aux = {}
        for par, ps in iteritems(self.scheme):
            for pos in ps['pos']:
                l = aux.setdefault(pos, [])
                l.append(par)
        res, pivot = {}, 0
        for pos in range(min(aux), max(aux) + 1):
            if pos in aux:
                res[pivot] = sorted(aux[pos])
                pivot += 1
        self.positions = res

    def __call__(self, args, kwargs):
        '''Consolidate in `kwargs` all actual parameters.

        :param args: The positional arguments received by the calling function.

        :param kwargs: The keyword arguments received by the calling function.

        '''
        from xoutil.eight import iteritems
        assert isinstance(args, tuple) and isinstance(kwargs, dict)

        def clean(name):
            '''If argument with name is not yet assigned.'''
            return name not in kwargs

        def settle(name, value):
            '''Settle a value if not yet assigned, raises an error if not.'''
            if clean(name):
                kwargs[str(name)] = value
            else:
                msg = 'Got multiple values for "{}" argument: "{}" and "{}"!'
                raise TypeError(msg.format(name, value, kwargs[name]))

        def solve_aliases():
            '''Solve keyword arguments that have aliases.'''
            from xoutil import Unset
            for par, ps in iteritems(self.scheme):
                for alias in ps['aliases']:
                    value = kwargs.pop(alias, Unset)
                    if value is not Unset:
                        settle(par, value)

        def check_kwargs():
            '''Check all formal keyword arguments.'''
            from xoutil.values import valid
            for key, arg in iteritems(kwargs):
                if key in self.scheme:
                    checker = self.scheme[key]['checker']
                    value = checker(arg)
                    if valid(value):
                        kwargs[str(key)] = value
                    else:
                        msg = 'Invalid argument value "{}": "{}"!'
                        raise ValueError(msg.format(key, arg))
                elif self.strict:
                    msg = 'Invalid keyword argument "{}": "{}"!'
                    raise ValueError(msg.format(key, arg))

        def solve_results():
            '''Assign default values for missing arguments.'''
            from xoutil.values import valid
            for par, ps in iteritems(self.scheme):
                if clean(par):
                    default = ps['default']
                    if valid(default):
                        kwargs[str(par)] = default
                    else:
                        msg = 'Missing required argument "{}"!'
                        raise TypeError(msg.format(par))

        def get_valid():
            '''Get the valid parameter name in current position pivot.

            Return a tuple (name, value) if valid.

            '''
            from xoutil.values import valid
            names = positions[pivot]
            i, count = 0, len(names)
            res = ()
            while not res and i < count:
                name = names[i]
                if clean(name):
                    checker = self.scheme[name]['checker']
                    value = checker(arg)
                    if valid(value):
                        res = (name, value)
                i += 1
            return res

        def get_duplicate():
            '''Get a possible all not settled valid parameter names.'''
            from xoutil.values import valid
            res = None
            pos = last_pivot
            while not res and pos < len(positions):
                names = positions[pos]
                i = 0
                while not res and i < len(names):
                    name = names[i]
                    if name not in settled:
                        checker = self.scheme[name]['checker']
                        value = checker(arg)
                        if valid(value):
                            res = name
                    i += 1
                pos += 1
            return res

        solve_aliases()
        check_kwargs()
        # Solve positional arguments
        settled = set()
        positions = self.positions
        positionals = {p for p, ps in iteritems(self.scheme) if ps['pos']}
        max_args = len({name for name in positionals if clean(name)})
        i, count = 0, len(args)
        pivot = last_pivot = 0
        if count <= max_args:
            while i < count and pivot < len(positions):
                arg = args[i]
                res = get_valid()
                if res:
                    name, value = res
                    settle(name, value)
                    settled.add(name)
                    last_pivot = pivot
                    i += 1
                else:
                    pivot += 1
            if i == count:
                solve_results()
            else:
                from xoutil.eight import typeof
                dup = get_duplicate()
                extra = 'duplicate "{}" '.format(dup) if dup else ''
                msg = ('Invalid {}argument "{}" at position "{}" of type '
                       '"{}".')
                tname = typeof(arg).__name__
                raise TypeError(msg.format(extra, arg, i, tname))
        else:
            msg = 'Expecting at most {} positional arguments ({} given)!'
            raise TypeError(msg.format(max_args, count))


if __name__ == '__main__':
    print('Testing module "xoutil.params"')

    import sys
    from xoutil.eight import string_types
    from xoutil.values import file_coerce, positive_int_coerce

    sample_scheme = {
        'stream': (file_coerce, {0, 3}, {'output'}, sys.stdout),
        'indent': (positive_int_coerce, {1}, 1),
        'width': (positive_int_coerce, {2}, {'max_width'}, 79),
        'newline': (string_types, '\n'), }

    def test(*args, **kwargs):
        print('-'*80)
        print(">>>", args, "--", kwargs)
        try:
            conformer(args, kwargs)
            print("...", kwargs)
        except BaseException as error:
            print("???", '{}:'.format(type(error).__name__), error)

    conformer = ParamConformer(sample_scheme)

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

    conformer = ParamConformer(sample_scheme, __strict__=True)

    test(80, indent=4, extra="I'm not OK!")
