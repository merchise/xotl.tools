#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Parse URLs into components.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)

from xoutil.eight import python_version


if python_version == 3:
    # Python 3 __all__ in Python 2 urlparse
    from urllib.parse import (    # noqa
        ParseResult, SplitResult, parse_qs, parse_qsl, unquote, urldefrag,
        urljoin, urlparse, urlsplit, urlunparse, urlunsplit)

    # Python 3 __all__ in Python 2 urllib
    from urllib.parse import (    # noqa
        quote, quote_plus, unquote_plus, urlencode)

    # Python 3 __all__ but not in Python 2
    from urllib.parse import (    # noqa
        DefragResult, DefragResultBytes, ParseResultBytes, SplitResultBytes,
        quote_from_bytes, unquote_to_bytes)

    # Not in Python 3 __all__ in Python 2 urlparse
    try:
        from urllib.parse import clear_cache   # noqa
    except ImportError:
        pass

    # Not in Python 3 __all__ in Python 2 urllib
    try:
        from urllib.parse import(    # noqa
            splitattr, splithost, splitnport, splitpasswd, splitport,
            splitquery, splittag, splittype, splituser, splitvalue, unwrap)
    except ImportError:
        pass

    # Python 3 Data in Python 2 urlparse
    try:
        from urllib.parse import(    # noqa
            MAX_CACHE_SIZE, non_hierarchical, scheme_chars, uses_fragment,
            uses_netloc, uses_params, uses_query, uses_relative)
    except ImportError:
        pass
else:
    # Python 3 __all__ in Python 2 urlparse
    from urlparse import (    # noqa
        ParseResult, SplitResult, parse_qs, parse_qsl, unquote, urldefrag,
        urljoin, urlparse, urlsplit, urlunparse, urlunsplit)

    # Python 3 __all__ in Python 2 urllib
    from urllib import (    # noqa
        quote, quote_plus, unquote_plus, urlencode)

    # Python 3 __all__ but not in Python 2
    DefragResult = DefragResultBytes = tuple
    ParseResultBytes = SplitResultBytes = tuple

    def quote_from_bytes(bs, safe='/'):
        '''Like `quote`, but accepts a bytes object rather than a str.

        quote_from_bytes(b'abc def?') -> 'abc%20def%3f'

        Also it does not perform string-to-bytes encoding.  It always
        returns an ASCII string.

        In this case, it works also with unicode and buffers.

        '''
        from xoutil.eight import string
        if isinstance(bs, (bytes, unicode, buffer)):
            return quote(string.force(bs), safe=safe)
        else:
            raise TypeError("quote_from_bytes() expected bytes")

    def unquote_to_bytes(string):
        '''unquote_to_bytes('abc%20def') -> b'abc def'.'''
        from xoutil.eight import string
        return string.force(unquote(string))

    # Not in Python 3 __all__ in Python 2 urlparse
    try:
        from urlparse import clear_cache   # noqa
    except ImportError:
        pass

    # Not in Python 3 __all__ in Python 2 urllib
    try:
        from urllib import(    # noqa
            splitattr, splithost, splitnport, splitpasswd, splitport,
            splitquery, splittag, splittype, splituser, splitvalue, unwrap)
    except ImportError:
        pass

    # Python 3 Data in Python 2 urlparse
    try:
        from urlparse import(    # noqa
            MAX_CACHE_SIZE, non_hierarchical, scheme_chars, uses_fragment,
            uses_netloc, uses_params, uses_query, uses_relative)
    except ImportError:
        pass


del python_version
