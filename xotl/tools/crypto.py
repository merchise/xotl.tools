#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""General security tools.

Adds the ability to generate new passwords using a source pass-phrase and a
secury strong level.

"""


__all__ = (
    "PASS_PHRASE_LEVEL_BASIC",
    "PASS_PHRASE_LEVEL_MAPPED",
    "PASS_PHRASE_LEVEL_MAPPED_MIXED",
    "PASS_PHRASE_LEVEL_MAPPED_DATED",
    "PASS_PHRASE_LEVEL_STRICT",
    "generate_password",
)


#: The most basic level (less ) for the password generation.
PASS_PHRASE_LEVEL_BASIC = 0

#: A level for simply mapping of several chars.
PASS_PHRASE_LEVEL_MAPPED = 1

#: Another "stronger" mapping level.
PASS_PHRASE_LEVEL_MAPPED_MIXED = 2

#: Appends the year after mapping.
PASS_PHRASE_LEVEL_MAPPED_DATED = 3

#: Totally scramble the result, making very hard to predict the result.
PASS_PHRASE_LEVEL_STRICT = 4

#: The default level for `generate_password`:func:
DEFAULT_PASS_PHRASE_LEVEL = PASS_PHRASE_LEVEL_MAPPED_DATED


#: A mapping from names to standards levels.  You may use these strings as
#: arguments for `level` in `generate_password`:func:.
PASS_LEVEL_NAME_MAPPING = {
    "basic": PASS_PHRASE_LEVEL_BASIC,
    "mapped": PASS_PHRASE_LEVEL_MAPPED,
    "mixed": PASS_PHRASE_LEVEL_MAPPED_MIXED,
    "dated": PASS_PHRASE_LEVEL_MAPPED_DATED,
    "random": PASS_PHRASE_LEVEL_STRICT,
}


BASIC_PASSWORD_SIZE = 4  # bytes

#: An upper limit for generated password length.
MAX_PASSWORD_SIZE = 512


SAMPLE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


def _normalize_level(level):
    """Normalize the `level` argument.

    If passed a string, it must be a key in `PASS_LEVEL_NAME_MAPPING`:obj:.
    Otherwise it must be a valid level number.

    """
    if isinstance(level, str):
        return PASS_LEVEL_NAME_MAPPING[level]
    else:
        return level


def generate_password(pass_phrase, level=DEFAULT_PASS_PHRASE_LEVEL):
    """Generate a password from a source `pass-phrase` and a security `level`.

    :param pass_phrase: String pass-phrase to be used as base of password
                        generation process.

    :param level: Numerical security level (the bigger the more secure, but
                  don't exaggerate!).

    When `pass_phrase` is a valid string, `level` means a generation method.
    Each level implies all other with an inferior numerical value.

    There are several definitions with numerical values for `level` (0-4):

    `PASS_PHRASE_LEVEL_BASIC`:data:

        Generate the same pass-phrase, just removing invalid characters and
        converting the result to lower-case.

    `PASS_PHRASE_LEVEL_MAPPED`:data:

        Replace some characters with new values: ``'e'->'3'``, ``'i'->'1'``,
        ``'o'->'0'``, ``'s'->'5'``.

    `PASS_PHRASE_LEVEL_MAPPED_MIXED`:data:

        Consonants characters before 'M' (included) are converted to
        upper-case, all other are kept lower-case.

    `PASS_PHRASE_LEVEL_MAPPED_DATED`:data:

        Adds a suffix with the year of current date ("<YYYY>").

    `PASS_PHRASE_LEVEL_STRICT`:data:

        Randomly scramble previous result until unbreakable strong password is
        obtained.

    If `pass_phrase` is ``None`` or an empty string, generate a "secure salt"
    (a password not based in a source pass-phrase).  A "secure salt" is
    generated by scrambling the concatenation of a random phrases from the
    alphanumeric vocabulary.

    Returned password size is ``4*level`` except when a `pass-phrase` is given
    for `level` <= 4 where depend on the count of valid characters of
    `pass-phrase` argument, although minimum required is warranted.  When
    `pass-phrase` is ``None`` for `level` zero or negative, size ``4`` is
    assumed.  First four levels are considered weak.

    Maximum size is defined in the :data:`MAX_PASSWORD_SIZE` constant.

    Default level is :data:`PASS_PHRASE_LEVEL_MAPPED_DATED` when using a
    pass-phrase.

    """
    from random import randint, sample

    from xotl.tools.string import slugify

    level = _normalize_level(level)
    size = MAX_PASSWORD_SIZE + 1  # means, return all calculated
    required = min(max(level, 1) * BASIC_PASSWORD_SIZE, MAX_PASSWORD_SIZE)
    if pass_phrase:
        # PASS_PHRASE_LEVEL_BASIC
        res = slugify(pass_phrase, "", invalid_chars="_")
        if level >= PASS_PHRASE_LEVEL_MAPPED:
            for (old, new) in ("e3", "i1", "o0", "s5"):
                res = res.replace(old, new)
        if level >= PASS_PHRASE_LEVEL_MAPPED_MIXED:
            for new in "BCDFGHJKLM":
                old = new.lower()
                res = res.replace(old, new)
        if level >= PASS_PHRASE_LEVEL_MAPPED_DATED:
            from datetime import datetime

            today = datetime.today()
            res += today.strftime("%Y")
        if level >= PASS_PHRASE_LEVEL_STRICT:
            size = required
    else:
        size = required
        count = randint(BASIC_PASSWORD_SIZE, 2 * BASIC_PASSWORD_SIZE)
        res = "".join(sample(SAMPLE, count))
    if size <= MAX_PASSWORD_SIZE:
        if len(res) < size:
            needed = (size - len(res)) // BASIC_PASSWORD_SIZE + 1
            res += generate_password(None, needed)
        res = "".join(sample(res, size))
    return res[:size]
