# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xotl.http
#----------------------------------------------------------------------
# Copyright (c) 2011 Merchise Autrement
# All rights reserved.
#
# Author: Medardo Rodriguez
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#       
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#       
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on Jun 28, 2011

'''Utils for Web applications.'''


from __future__ import (division as _py3_division, print_function as _py3_print,
                        unicode_literals as _py3_unicode)



def slugify(s, entities=True, decimal=True, hexadecimal=True):
    '''
    Normalizes string, converts to lower-case, removes non-alpha characters,
    and converts spaces to hyphens.
    Parts from http://www.djangosnippets.org/snippets/369/
    
        >>> slugify(u"Manuel Vázquez Acosta")
        u'manuel-vazquez-acosta'
    '''
    import re, unicodedata
    from htmlentitydefs import name2codepoint
    if not isinstance(s, unicode):
        s = unicode(s)  # "smart_unicode" in orginal
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
