#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Functions and classes which help in opening URLs (mostly HTTP).

Authentication, redirections, cookies, and more.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_import)

from xoutil.eight import python_version


if python_version == 3:
    # Python 3 __all__ in Python 2 urllib
    from urllib.request import (    # noqa
        FancyURLopener, URLopener, getproxies, pathname2url, url2pathname,
        urlcleanup, urlopen, urlretrieve)

    # Python 3 __all__ in Python 2 urllib2
    from urllib.request import (    # noqa
        AbstractBasicAuthHandler, AbstractDigestAuthHandler, BaseHandler,
        CacheFTPHandler, FTPHandler, FileHandler, HTTPBasicAuthHandler,
        HTTPCookieProcessor, HTTPDefaultErrorHandler, HTTPDigestAuthHandler,
        HTTPErrorProcessor, HTTPHandler, HTTPPasswordMgr,
        HTTPPasswordMgrWithDefaultRealm, HTTPRedirectHandler, HTTPSHandler,
        OpenerDirector, ProxyBasicAuthHandler, ProxyDigestAuthHandler,
        ProxyHandler, Request, UnknownHandler, build_opener, getproxies,
        install_opener, url2pathname, urlopen)

    # Python 3 dir in Python 2 urllib
    try:
        from urllib.request import (    # noqa
            ftperrors, ftpwrapper, getproxies_environment, localhost,
            noheaders, proxy_bypass, proxy_bypass_environment, thishost)
    except ImportError:
        pass

    # Python 3 dir in Python 2 urllib2
    try:
        from urllib.request import (    # noqa
            AbstractHTTPHandler, ftpwrapper, localhost, parse_http_list,
            parse_keqv_list, proxy_bypass, request_host)
    except ImportError:
        pass

    # Python 3 data in Python 2 urllib
    try:
        from urllib.request import MAXFTPCACHE, ftpcache    # noqa
    except ImportError:
        pass

    # Not yet in Python 2.7
    try:
        from urllib.request import (    # noqa
            DataHandler, HTTPPasswordMgrWithPriorAuth)
    except ImportError:
        pass
else:
    # Python 3 __all__ in Python 2 urllib
    from urllib import (    # noqa
        FancyURLopener, URLopener, getproxies, pathname2url, url2pathname,
        urlcleanup, urlopen, urlretrieve)

    # Python 3 __all__ in Python 2 urllib2
    from urllib2 import (    # noqa
        AbstractBasicAuthHandler, AbstractDigestAuthHandler, BaseHandler,
        CacheFTPHandler, FTPHandler, FileHandler, HTTPBasicAuthHandler,
        HTTPCookieProcessor, HTTPDefaultErrorHandler, HTTPDigestAuthHandler,
        HTTPErrorProcessor, HTTPHandler, HTTPPasswordMgr,
        HTTPPasswordMgrWithDefaultRealm, HTTPRedirectHandler, HTTPSHandler,
        OpenerDirector, ProxyBasicAuthHandler, ProxyDigestAuthHandler,
        ProxyHandler, Request, UnknownHandler, build_opener, getproxies,
        install_opener, url2pathname, urlopen)

    # Python 3 dir in Python 2 urllib
    try:
        from urllib import (    # noqa
            ftperrors, ftpwrapper, getproxies_environment, localhost,
            noheaders, proxy_bypass, proxy_bypass_environment, thishost)
    except ImportError:
        pass

    # Python 3 dir in Python 2 urllib2
    try:
        from urllib2 import (    # noqa
            AbstractHTTPHandler, ftpwrapper, localhost, parse_http_list,
            parse_keqv_list, proxy_bypass, request_host)
    except ImportError:
        pass

    # Python 3 data in Python 2 urllib
    try:
        from urllib import MAXFTPCACHE, ftpcache    # noqa
    except ImportError:
        pass

    # Not yet in Python 2.7
    try:
        from urllib import (    # noqa
            DataHandler, HTTPPasswordMgrWithPriorAuth)
    except ImportError:
        try:
            from urllib2 import (    # noqa
                DataHandler, HTTPPasswordMgrWithPriorAuth)
        except ImportError:
            pass
    except ImportError:
        pass

del python_version
