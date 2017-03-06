`xoutil.eight`:mod: - Python 2 to Python 3 compatibility
========================================================

There is another module (`xoutil.future`:mod:) that is somewhat similar, but
not exactly: `~xoutil.eight`:mod: creates peer compatibility (stuffs that are
in both major version but in different syntax shapes); and
`~xoutil.future`:mod: contains extensions that are implemented in Python 3 (or
must be) but they are not currently supported at all in Python 2.

.. automodule:: xoutil.eight
   :members:


Tools
=====

.. automodule:: xoutil.eight.meta
   :members: metaclass

.. automodule:: xoutil.eight.io
   :members: is_file_like

.. automodule:: xoutil.eight.exceptions

.. automodule:: xoutil.eight.errors

.. automodule:: xoutil.eight.abc
