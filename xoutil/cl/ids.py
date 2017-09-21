#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.ids
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~] and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.

'''Utilities to obtain identifiers that are unique at different contexts.

Contexts could be global, host local or application local.  All standard
`uuid`:mod: tools are included in this one: `UUID`:class:, `uuid1`:func:,
`uuid3`:func:, `uuid4`:func:, `uuid5`:func:, `getnode`:func: and standard
UUIDs constants `NAMESPACE_DNS`, `NAMESPACE_URL`, `NAMESPACE_OID` and
`NAMESPACE_X500`.

This module also contains:

- `str_uuid`:func:\ : Return a string with a GUID representation, random if
  the argument is True, or a host ID if not.

- `slugify`:func:\ : Convert any object to a valid slug (mainly used with
  string parameters).

.. versionadded:: 1.7.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)


from uuid import (UUID, uuid1, uuid3, uuid4, uuid5, getnode,    # noqa
                  NAMESPACE_DNS, NAMESPACE_URL, NAMESPACE_OID, NAMESPACE_X500)


def str_uuid(random=False):
    '''Return a "Global Unique ID" as a string.

    :param random: If True, a random uuid is generated (does not use host id).

    '''
    fn = uuid4 if random else uuid1
    return '{}'.format(fn())


# TODO: integrate with 'xoutil.future.string.normalize_slug'
def slugify(value, *args, **kwargs):
    '''Return the string normal form, valid for slugs, for a given value.

    All values expecting strings are coerced using the following methodology:
    normalize all non-ascii to valid characters using unicode 'NFKC', converts
    to lower-case and translate all invalid chars (including white-spaces) to
    the character defined as `replacement` (normally a hyphen, see below).

    In all values expecting sets repeated characters will be removed.

    In the result value, all repeated replacement occurrences will be striped;
    as well as those in the leading and trailing positions.

    :param value: The source value to slugify.  It's the first positional
           argument and always is required.

    :param replacement: A character to be used as replacement for unwanted
           characters.

           Could be given as a name argument or in the second positional
           argument (index 0 in `args`).  Default value is a hyphen ('-').

    :param invalid_chars: Characters to be considered invalid.  There is a
           default set of valid characters which are kept in the resulting
           slug.  Characters given in this parameter are removed from the
           resulting valid character set (see next parameter).

           Extra argument values can be used for compatibility with
           `invalid_underscore` argument in deprecated `normalize_slug`:func:
           xoutil function:

           - ``True`` is a synonymous of underscore ``"_"``.

           - ``False`` or ``None``: An empty set.

           Could be given as a name argument or in the third positional
           argument (index 1 in `args`).  Default value is an empty set.

    :param valid_chars: A collection of extra valid characters.  Default set of
           valid characters are alpha-numeric and the underscore (those that
           fulfill with the regular expression ``[_a-z0-9]``).  All characters
           not convertible to ascii are ignored.

           This argument is processed before `invalid_chars`.

           Could be given only as a name argument.  Default value is an empty
           set.

    :param smalls: Management for small parts, those with 3 or less
           characters.  Next, all possible values for this argument:

           1. ``None``, ``False`` or the string ``"crop"``: remove small
              parts.

           2. ``True`` or the string ``"keep"``: maintain small parts; this is
              the default value.

           3. The string ``"join"``: small parts are joined to the smallest
              of its consecutive parts.

    Parameters `value` and `replacement` could be of any (non-string) type,
    these values are normalized and converted to lower-case ASCII strings.

    Examples::

      >>> slugify('  Á.e i  Ó  u  ') == 'a-e-i-o-u'
      True

      >>> slugify('  Á.e i  Ó  u  ', '.', invalid_chars='AU') == 'e.i.o'
      True

      >>> slugify('  Á.e i  Ó  u  ', valid_chars='.') == 'a.e-i-o-u'
      True

      >>> slugify('_x', '_') == '_x'
      True

      >>> slugify('-x', '_') == 'x'
      True

      >>> slugify(None) == 'none'
      True

      >>> slugify(1 == 1)  == 'true'
      True

      >>> slugify(1.0) == '1-0'
      True

      >>> slugify(135) == '135'
      True

      >>> slugify(123456, replacement='', invalid_chars='52') == '1346'
      True

      >>> slugify('_x', replacement='_') == '_x'
      True

    .. versionadded:: 1.7.0 To deprecate `normalize_slug` and add
                      `crop_smalls` parameter.

    '''
    import re
    from xoutil.eight import string_types
    from xoutil.cl import compose, istype
    from xoutil.cl.simple import not_false, ascii_coerce, lower_ascii_coerce
    from xoutil.params import ParamManager
    # local functions
    getarg = ParamManager(args, kwargs)
    _str = compose(not_false(''), istype(string_types))
    _ascii = compose(_str, ascii_coerce)
    _lascii = compose(_str, lower_ascii_coerce)
    _set = compose(_ascii, lambda v: ''.join(set(v)))
    _esc = compose(_set, lambda v: re.escape(v))

    def _from_iter(v):
        return ''.join(i for i in v)

    replacement = getarg('replacement', 0, default='-', coercers=string_types)
    invalid_chars = getarg('invalid_chars', 0, default='', coercers=_ascii)
    valid_chars = getarg('valid_chars', 0, default='', coercers=_ascii)
    if invalid_chars is True:
        # Backward compatibility with former `invalid_underscore` argument
        invalid_chars = '_'
    elif invalid_chars in {None, False}:
        invalid_chars = ''
    else:
        if not isinstance(invalid_chars, string_types):
            invalid_chars = ''.join(i for i in invalid_chars)
        invalid_chars = _esc(_lascii(invalid_chars))
    if not isinstance(valid_chars, string_types):
        valid_chars = _from_iter(valid_chars)
    valid_chars = _esc(re.sub(r'[0-9a-b]+', '', _lascii(valid_chars)))
    # calculate result
    res = _lascii(value)
    regex = re.compile(r'[^_a-z0-9%s]+' % valid_chars)
    repl = '\t' if replacement else ''
    res = regex.sub(repl, res)
    if invalid_chars:
        regex = re.compile(r'[%s]+' % invalid_chars)
        res = regex.sub(repl, res)
    if repl:
        r = {'r': r'%s' % re.escape(repl)}
        regex = re.compile(r'(%(r)s){2,}' % r)
        res = regex.sub(repl, res)
        regex = re.compile(r'(^%(r)s+|%(r)s+$)' % r)
        res = regex.sub('', res)
        regex = re.compile(r'[\t]' % r)
        res = regex.sub(replacement, res)
    return res
