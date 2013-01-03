# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xotl.http
#----------------------------------------------------------------------
# Copyright (c) 2011 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Jun 28, 2011

'''Utils for Web applications.'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)


def slugify(s, entities=True, decimal=True, hexadecimal=True):
    '''
    Normalizes string, converts to lower-case, removes non-alpha characters,
    and converts spaces to hyphens.

    Parts from http://www.djangosnippets.org/snippets/369/

        >>> slugify(u"Manuel Vázquez Acosta")
        u'manuel-vazquez-acosta'

    If `s` and `entities` is True (the default) all HTML entities
    are replaced by its equivalent character before normalization::

        >>> slugify(u"Manuel V&aacute;zquez Acosta")
        u'manuel-vazquez-acosta'

    If `entities` is False, then no HTML-entities substitution is made::

        >>> slugify(u"Manuel V&aacute;zquez Acosta", entities=False)
        u'manuel-v-aacute-zquez-acosta'

    If `decimal` is True, then all entities of the form ``&#nnnn`` where
    `nnnn` is a decimal number deemed as a unicode codepoint, are replaced by
    the corresponding unicode character::

        >>> slugify(u'Manuel V&#225;zquez Acosta')
        u'manuel-vazquez-acosta'

        >>> slugify(u'Manuel V&#225;zquez Acosta', decimal=False)
        u'manuel-v-225-zquez-acosta'


    If `hexadecimal` is True, then all entities of the form ``&#nnnn`` where
    `nnnn` is a hexdecimal number deemed as a unicode codepoint, are replaced
    by the corresponding unicode character::

        >>> slugify(u'Manuel V&#x00e1;zquez Acosta')
        u'manuel-vazquez-acosta'

        >>> slugify(u'Manuel V&#x00e1;zquez Acosta', hexadecimal=False)
        u'manuel-v-x00e1-zquez-acosta'

    '''
    import re
    import unicodedata
    from htmlentitydefs import name2codepoint
    from xoutil.string import _unicode, safe_decode
    if not isinstance(s, _unicode):
        s = safe_decode(s)  # "smart_unicode" in orginal
    if entities:
        s = re.sub('&(%s);' % '|'.join(name2codepoint),
                   lambda m: unichr(name2codepoint[m.group(1)]), s)
    if decimal:
        try:
            s = re.sub('&#(\d+);', lambda m: unichr(int(m.group(1))), s)
        except:
            pass
    if hexadecimal:
        try:
            s = re.sub('&#x([\da-fA-F]+);',
                       lambda m: unichr(int(m.group(1), 16)), s)
        except:
            pass
    #translate
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
    #replace unwanted characters
    s = re.sub(r'[^-_a-z0-9]+', '-', s.lower())
    #remove redundant -
    s = re.sub('-{2,}', '-', s).strip('-')
    return s


__all__ = (b'slugify',)
