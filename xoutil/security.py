# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.security
#----------------------------------------------------------------------
# Copyright (c) 2014 Merchise Autrement
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-04-22

'''General security tools.

Adds the ability to generate new passwords using a source pass-phrase and a
secury strong level.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)


from xoutil.names import strlist as strs
__all__ = strs('PASS_PHRASE_METHOD_BASIC', 'PASS_PHRASE_METHOD_MAPPED',
               'PASS_PHRASE_METHOD_MAPPED_SALTED',
               'PASS_PHRASE_METHOD_STRICT', 'create_password')
del strs


PASS_PHRASE_METHOD_BASIC = 0
PASS_PHRASE_METHOD_MAPPED = 1
PASS_PHRASE_METHOD_MAPPED_SALTED = 2
PASS_PHRASE_METHOD_STRICT = 3

DEFAULT_PASS_PHRASE_METHOD = PASS_PHRASE_METHOD_MAPPED_SALTED


PythonZen = [        # Used to strict password generator
    "Beautiful is better than ugly",
    "Explicit is better than implicit",
    "Simple is better than complex",
    "Complex is better than complicated",
    "Flat is better than nested",
    "Sparse is better than dense",
    "Readability counts",
    "Special cases aren't special enough to break the rules",
    "Although practicality beats purity",
    "Errors should never pass silently",
    "Unless explicitly silenced",
    "In the face of ambiguity, refuse the temptation to guess",
    "There should be one-- and preferably only one --obvious way to do it",
    "Although that way may not be obvious at first unless you're Dutch",
    "Now is better than never",
    "Although never is often better than *right* now",
    "If the implementation is hard to explain, it's a bad idea",
    "If the implementation is easy to explain, it may be a good idea",
    "Namespaces are one honking great idea -- let's do more of those"]


def create_password(pass_phrase, method=DEFAULT_PASS_PHRASE_METHOD):
    '''Generate a new password, given a source `pass-phrase` and a `method`.

    :param pass_phrase: Source pass-phrase as string
    :param method: Method with the security strong level

    Several methods could be applied:

    - PASS_PHRASE_METHOD_BASIC: Generate the same pass-phrase, just removing
      invalid characters for passwords.  This method is very insecure; so,
      very insecure.

    - PASS_PHRASE_METHOD_MAPPED: Execute previous method and map some
      characters.  'a' -> '@', 'e' -> '3', 'i' -> 1, 'o' -> '0', 's' -> '5'.
      All consonants before and including 'M' are converted to upper-case, the
      rest are in lower-case.

    - PASS_PHRASE_METHOD_MAPPED_SALTED: Same as previous method adding a
      suffix with "<YYYY>" (year of current date).

    - PASS_PHRASE_METHOD_STRICT: Statistically generated using a unbreakable
      algorithms.

    All methods but last are executed incrementally: each one implies all
    previous.  The default method is `PASS_PHRASE_METHOD_MAPPED_SALTED` and
    will be the one used in the security mechanism for allowing developers to
    modify production data-base in order to use them in development
    environment.

    '''
    # Now is implemented only the default method.
    from xoutil.string import normalize_slug
    res = normalize_slug(pass_phrase, '').lower()
    if len(res) > 3:
        if method > PASS_PHRASE_METHOD_BASIC:
            for (old, new) in ('a@', 'e3', 'i1', 'o0', 's5'):
                res = res.replace(old, new)
            for new in "BCDFGHJKLM":
                old = new.lower()
                res = res.replace(old, new)
            if method > PASS_PHRASE_METHOD_MAPPED:
                from datetime import datetime
                today = datetime.today()
                res += today.strftime("%Y")
                if method > PASS_PHRASE_METHOD_MAPPED_SALTED:
                    from random import sample, randint
                    aux = sample(res, len(res))
                    while len(aux) < 32:
                        rnd = str(randint(1000, 9999))
                        rnd += PythonZen[randint(1, len(PythonZen)) - 1]
                        rnd = normalize_slug(rnd, '')
                        aux.extend(sample(rnd, len(rnd)))
                    res = ''.join(aux)[0:32]
        return res
    else:
        raise ValueError("Pass-phrase too short: %s" % pass_phrase)
