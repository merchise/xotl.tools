`xoutil.eight.urllib`:mod: - Compatibility to Python's `urllib` module
======================================================================

.. automodule:: xoutil.eight.urllib

.. versionadded:: 1.8.4

``urllib`` is maybe the hardest module to use from Python 2/3 compatible code.
You may like to use Requests_ instead.  In this implementation is used the
module structure in Python 3 but only the functions that are already in both
versions of Python are exposed for sure.

``urllib`` is a package that collects several modules for working with URLs,
in ``xoutil`` these structures are exposed inner `xoutil.eight.urllib`:mod:\ :

- ``request`` for opening and reading URLs.

- ``error` containing the exceptions raised by ``request``

- ``parse`` for parsing URLs.

- ``robotparser`` for parsing robots.txt files

.. _requests: http://python-requests.org
