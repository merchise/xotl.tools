===================================================================
 `xotl.tools.params`:mod: -- Tools for managing function arguments
===================================================================

.. automodule:: xotl.tools.params

.. testsetup::

   from xotl.tools.params import *


Examples
========

In next example, the parameter key-named "stream" could be also passed as name
"output", must be a file, default value is ``stdout``, and if passed as
positional, could be the first or the last one.


  >>> import sys
  >>> from io import IOBase
  >>> def positive_int(value):
  ...     value = int(value)
  ...     return value if value >= 0 else False
  >>> from xotl.tools.params import ParamScheme as scheme, ParamSchemeRow as row

  >>> sample_scheme = scheme(
  ...     row('stream', 0, -1, 'output', default=sys.stdout, coerce=(IOBase,)),
  ...     row('indent', 0, 1, default=1, coerce=positive_int),
  ...     row('width', 0, 1, 2, 'max_width', default=79, coerce=positive_int),
  ...     row('newline', default='\n', coerce=(str, )))


Some tests::

  >>> def test(*args, **kwargs):
  ...     return sample_scheme(args, kwargs)

  >>> test(4, 80)
  {'indent': 4,
   'newline': '\n',
   'stream': <open file '<stdout>', mode 'w' at 0x7f927b32b150>,
   'width': 80}

  >>> test(2, '80')    # Because positive int coercer use valid string values
  {'indent': 2,
   'newline': '\n',
   'stream': <open file '<stdout>', mode 'w' at 0x7f927b32b150>,
   'width': 80}

  >>> test(sys.stderr, 4, 80)
  {'indent': 4,
   'newline': '\n',
   'stream': <open file '<stderr>', mode 'w' at 0x7f927b32b1e0>,
   'width': 80}

  >>> test(4, sys.stderr, newline='\n\r')
  {'indent': 4,
   'newline': '\n\r',
   'stream': <open file '<stderr>', mode 'w' at 0x7f927b32b1e0>,
   'width': 79}

  >>> sample_scheme((4, 80), {'extra': 'extra param'}, strict=False)
  {'extra': 'extra param',
   'indent': 4,
   'newline': '\n',
   'stream': <open file '<stdout>', mode 'w' at 0x7f3c6815c150>,
   'width': 80}

The examples above describe the deprecated schema API, retained until 4.0.0.
New code should declare parameters explicitly and let Python validate calls.
For example, `xotl.tools.string.slugify`:func: uses named parameters and keyword-only
options rather than ``ParamManager``.  See its signature for the supported calling convention.


Module Members
==============

.. autofunction:: issue_9137

.. autofunction:: check_count

.. autofunction:: pop_keyword_arg

.. autofunction:: pop_keyword_values

.. autoclass:: ParamManager
   :members: __init__, __call__, remainder

.. autoclass:: ParamScheme
   :members: defaults, __call__, __len__, __getitem__, __iter__

.. autoclass:: ParamSchemeRow
   :members: key, default, __call__
