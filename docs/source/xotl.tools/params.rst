===================================================================
 `xotl.tools.params`:mod: -- Tools for managing function arguments
===================================================================

.. automodule:: xotl.tools.params


Examples
========

In next example, the parameter key-named "stream" could be also passed as name
"output", must be a file, default value is ``stdout``, and if passed as
positional, could be the first or the last one.


  >>> import sys
  >>> from xotl.tools.values import file_coerce as is_file
  >>> from xotl.tools.values import positive_int_coerce as positive_int
  >>> from xotl.tools.params import ParamScheme as scheme, ParamSchemeRow as row

  >>> sample_scheme = scheme(
  ...     row('stream', 0, -1, 'output', default=sys.stdout, coerce=is_file),
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

Another way of use this is through a `ParamManager`:class: instance, using the
actual arguments of a function to create it::

  >>> def slugify(value, *args, **kwds):
  ...     from xotl.tools.params import ParamManager
  ...     getarg = ParamManager(args, kwds)
  ...     replacement = getarg('replacement', 0, default='-',
  ...                          coercers=(str, ))
  ...     invalid_chars = getarg('invalid_chars', 'invalid', 'invalids', 0,
  ...                            default='', coercers=_ascii)
  ...     valid_chars = getarg('valid_chars', 'valid', 'valids', 0,
  ...                          default='', coercers=_ascii)
  ...     # And so on.

Notice that each call has the same protocol than a parameter definition row
(see `ParamSchemeRow`:class:).


Module Members
==============

.. autofunction:: issue_9137

.. autofunction:: check_count

.. autofunction:: check_default

.. autofunction:: single

.. autofunction:: pop_keyword_arg

.. autofunction:: pop_keyword_values

.. autoclass:: ParamManager
   :members: __init__, __call__, remainder

.. autoclass:: ParamScheme
   :members: defaults, __call__, __len__, __getitem__, __iter__

.. autoclass:: ParamSchemeRow
   :members: key, default, __call__
