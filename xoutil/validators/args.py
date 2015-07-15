# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.validators.args
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


'''This validator will check for function parameter passing.

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
  value `Invalid` is used to specify that the parameter is required.

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

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)


from xoutil.logical import Logical as InvalidType

Invalid = InvalidType('Invalid')


# Scheme concept validators: Each one checks if a value is compliant or not
# with determined scheme concept.


def _is_checker(value):
    '''Determine if a value is a position definition or not.'''
    from xoutil.eight import callable
    if isinstance(value, type):
        value = (value, )
    if isinstance(value, tuple) and all(isinstance(v, type) for v in value):
        def inner(arg):
            return arg if isinstance(arg, value) else Invalid
        types = '_'.join(t.__name__ for t in value)
        inner.__name__ = str('type_checker__{}'.format(types))
        return inner
    elif callable(value):
        def inner(arg):
            try:
                return value(arg)
            except BaseException:
                return Invalid
        inner.__name__ = getattr(value, '__name__', str('callable'))
        return inner
    else:
        return Invalid


def _is_pos(value):
    '''Determine if a value is a position definition or not.'''
    valid = lambda p: isinstance(p, int) and p >= 0
    if isinstance(value, set) and all(valid(p) for p in value):
        return value
    else:
        return Invalid


def _is_aliases(value):
    '''Determine if a value is an aliases definition or not.'''
    from .identifiers import is_valid_identifier as valid
    if isinstance(value, set) and all(valid(a) for a in value):
        return value
    else:
        return Invalid


_identity = lambda arg: arg
_is_def = _identity

_CONCEPT_NAMES = ('checker', 'pos', 'aliases', 'default')
_CONCEPT_VALIDATORS = (_is_checker, _is_pos, _is_aliases, _is_def)
_CONCEPT_DEFAULTS = (_identity, set(), set(), Invalid)

del _is_checker, _is_pos, _is_aliases, _is_def


class ParamConformer(object):
    '''Standardize actual parameters using a scheme.'''
    __slots__ = ('scheme', 'positions', 'strict')

    def __init__(self, scheme, strict=False):
        '''Create the conformer.

        :param scheme: The parameters scheme definition.  See the module
               documentation for more information.

        :param strict: If True, only scheme definitions could be used as
               actual arguments.

        '''
        self._formalize_scheme(scheme)
        self._normalize_positions()
        self.strict = strict

    def _formalize_scheme(self, scheme):
        '''Formalize scheme in a more precise internal dictionary.'''
        from xoutil import Unset
        from xoutil.collections import Mapping
        from xoutil.eight import zip
        from .identifiers import is_valid_identifier
        parsers = {n: c for n, c in zip(_CONCEPT_NAMES, _CONCEPT_VALIDATORS)}
        defaults = {n: c for n, c in zip(_CONCEPT_NAMES, _CONCEPT_DEFAULTS)}
        if scheme and isinstance(scheme, Mapping):
            scheme = dict(scheme)
            self.scheme = scheme
            for par in scheme:
                if is_valid_identifier(par):
                    par = str(par)
                    new = dict.fromkeys(_CONCEPT_NAMES, Unset)
                    ps = scheme[par]
                    if not isinstance(ps, tuple):
                        ps = (ps,)
                    for value in ps:
                        i, ok = 0, False
                        while i < len(_CONCEPT_NAMES) and not ok:
                            concept = _CONCEPT_NAMES[i]
                            if new[concept] is Unset:
                                parser = parsers[concept]
                                v = parser(value)
                                if v is not Invalid:
                                    ok = True
                                    new[concept] = v
                            i += 1
                        if not ok:
                            bads = ps[i - 1:]
                            msg = ('Invalid values "{}" for parameter "{}".')
                            raise ValueError(msg.format(bads, par))
                    # Complete values
                    for concept in _CONCEPT_NAMES:
                        if new[concept] is Unset:
                            new[concept] = defaults[concept]
                    default = new['default']
                    if default is not Invalid:
                        checker = new['checker']
                        checked = checker(default)
                        if checked is Invalid:
                            msg = ('Default value "{}" for parameter "{}" is '
                                   'checked invalid.')
                            raise ValueError(msg.format(default, par))
                    scheme[par] = new
                else:
                    msg = ('Keyword argument must be a valid Python '
                           'identifier, not "{}".')
                    raise ValueError(msg.format(par))
            self._check_duplicate_aliases()
        else:
            msg = 'Invalid scheme definition "{}": expecting a dictionary.'
            raise ValueError(msg.format(scheme))

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
            for key, arg in iteritems(kwargs):
                if key in self.scheme:
                    checker = self.scheme[key]['checker']
                    value = checker(arg)
                    if value is not Invalid:
                        kwargs[str(key)] = value
                    else:
                        msg = 'Invalid argument value "{}": "{}"!'
                        raise ValueError(msg.format(key, arg))
                elif self.strict:
                    msg = 'Invalid keyword argument "{}": "{}"!'
                    raise ValueError(msg.format(key, arg))

        def solve_results():
            '''Assign default values for missing arguments.'''
            for par, ps in iteritems(self.scheme):
                if clean(par):
                    default = ps['default']
                    if default is not Invalid:
                        kwargs[str(par)] = default
                    else:
                        msg = 'Missing required argument "{}"!'
                        raise TypeError(msg.format(par))

        def get_valid():
            '''Get the valid parameter name in current position pivot.

            Return a tuple (name, value) if valid.

            '''
            names = positions[pivot]
            i, count = 0, len(names)
            res = ()
            while not res and i < count:
                name = names[i]
                if clean(name):
                    checker = self.scheme[name]['checker']
                    value = checker(arg)
                    if value is not Invalid:
                        res = (name, value)
                i += 1
            return res

        def get_duplicate():
            '''Get a possible all not settled valid parameter names.'''
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
                        if value is not Invalid:
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
                dup = get_duplicate()
                extra = 'duplicate "{}" '.format(dup) if dup else ''
                msg = ('Invalid {}argument "{}" at position "{}" of type '
                       '"{}".')
                tname = type(arg).__name__
                raise TypeError(msg.format(extra, arg, i, tname))
        else:
            msg = 'Expecting at most {} positional arguments ({} given)!'
            raise TypeError(msg.format(max_args, count))


if __name__ == '__main__':
    print('Testing module "xoutil.validators.args"')

    import sys
    from xoutil.eight import string_types

    def check_file_like(arg):
        from xoutil.eight.io import is_file_like
        return arg if is_file_like(arg) else Invalid

    def check_positive_int(arg):
        from xoutil.eight import integer_types, string_types
        if isinstance(arg, integer_types):
            return arg if arg >= 0 else Invalid
        elif isinstance(arg, string_types):
            try:
                arg = int(arg)
                return arg if arg >= 0 else Invalid
            except ValueError:
                return Invalid
        else:
            return Invalid

    sample_scheme = {
        'stream': (check_file_like, {0, 3}, {'output'}, sys.stdout),
        'indent': (check_positive_int, {1}, 1),
        'width': (check_positive_int, {2}, {'max_width'}, 79),
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

    conformer = ParamConformer(sample_scheme, strict=True)

    test(80, indent=4, extra="I'm OK!")
