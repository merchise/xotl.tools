#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.ids
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-08-25

'''Utilities to obtain identifiers that are unique at different contexts.

Contexts could be global, host local or application local.  All standard
`uuid`:mod: tools are included in this one: `UUID`:class:, `uuid1`:func:,
`uuid3`:func:, `uuid4`:func:, `uuid5`:func:, `getnode`:func:` and standard
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


def slugify(value, *args, **kwargs):
    '''Return the string normal form, valid for slugs, for a given value.

    All values expecting strings are coerced using the following methodology:
    normalize all non-ascii to valid characters using unicode 'NFKC', converts
    to lower-case and translate all invalids (including white-spaces) to the
    character defined as `replacement` (normally a hyphen, see below).

    In all values expecting sets repeated characters will be removed.

    In the result value, all repeated replacement occurrences will be striped;
    as well as those in the leading and trailing positions.

    :param value: The source value to slugify.  It's the first positional
           argument and always is required.

    :param replacement: A character to be used as replacement for unwanted
           characters.

           Could be given as a name argument or in the second positional
           argument (index 0 in `args`).  Default value is a hyphen ('-').

    :param invalids: Characters to be considered invalids.  There is a default
           set of valid characters which are kept in the resulting slug.
           Characters given in this parameter are removed from the resulting
           valid character set (see next parameter).

           Extra argument values can be used for compatibility with
           `invalid_underscore` argument in deprecated `normalize_slug`:func:
           xoutil function:

           - ``True`` is a synonymous of underscore ``"_"``.

           - ``False`` or ``None``: An empty set.

           Could be given as a name argument or in the third positional
           argument (index 1 in `args`).  Default value is an empty set.

    :param valids: A collection of extra valid characters.  Default set of
           valid characters are alpha-numeric and the underscore (those that
           fulfill with the regular expression ``[_a-z0-9]``).  All characters
           not convertible to ascii are ignored.

           This argument is processed before `invalids`.

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

      >>> slugify('  Á.e i  Ó  u  ', '.', invalids='AU') == 'e.i.o'
      True

      >>> slugify('  Á.e i  Ó  u  ', valids='.') == 'a.e-i-o-u'
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

      >>> slugify(123456, replacement='', invalids='52') == '1346'
      True

      >>> slugify('_x', replacement='_') == '_x'
      True

    .. versionadded:: 1.7.0 To deprecate `normalize_slug` and add
                      `crop_smalls` parameter.

    '''
    import re
    from xoutil.eight import string_types
    from xoutil.string import normalize_ascii as ascii
    # local functions
    lascii = lambda v: ascii(v).lower()
    _set = lambda v: ''.join(set(v))
    _esc = lambda v: re.escape(_set(v))
    _from_iter = lambda v: ''.join(i for i in v)
    # check and adjust arguments
    if replacement in (None, False):
        replacement = ''
    elif isinstance(replacement, string_types):
        replacement = ascii(replacement)    # TODO: or lascii?
    else:
        msg = '`replacement` (%s) must be a string or None, not `%s`.'
        raise TypeError(msg % (replacement, type(replacement)))
    if invalids is True:
        # Backward compatibility with former `invalid_underscore` argument
        invalids = '_'
    elif invalids in {None, False}:
        invalids = ''
    else:
        if not isinstance(invalids, string_types):
            invalids = _from_iter(invalids)
        invalids = _esc(lascii(invalids))
    if valids is None:
        valids = ''
    else:
        if not isinstance(valids, string_types):
            valids = _from_iter(valids)
        valids = _esc(re.sub(r'[0-9a-b]+', '', lascii(valids)))
    # calculate result
    res = lascii(value)
    regex = re.compile(r'[^_a-z0-9%s]+' % valids)
    repl = '\t' if replacement else ''
    res = regex.sub(repl, res)
    if invalids:
        regex = re.compile(r'[%s]+' % invalids)
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
