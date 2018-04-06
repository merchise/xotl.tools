:orphan:

.. |py-string-ambiguity| replace:: String Ambiguity in Python
.. _py-string-ambiguity:

|py-string-ambiguity|
=====================

.. note:: This document is targeted to a version of xoutil that works in both
          Python 2 and Python 3.

In Python there are three semantic types when handling character strings:

1. .. _text-semantic:

   Text: by nature can be part of internationalization processes.  See
   Unicode__ for a standard for the representation, and handling of text in
   most of the world's writing systems.

   In Python 2 there is an special type `unicode`_ to process **text**,
   but sometimes `str`:class: is also used encoding the content; but in
   Python 3 ``str`` is always represented as **Unicode**.

2. .. _tech-semantic:

   Technical Strings: those used for for some special object names (classes,
   functions, modules, ...); the ``__all__`` definition in modules,
   identifiers, etc.  Those values most times requires necessarily to be
   instances of `str`:class: type.  Try next in Python 2::

     >>> class Foobar(object):
     ...    pass
     >>> Foobar.__name__ = u'foobar'
     TypeError: can only assign string to xxx.__name__, not 'unicode'

   In Python 2 ``str`` and ``bytes`` are synonymous; but in Python 3 are
   different types and ``bytes`` is exclusively used for **binary strings**.

3. .. _bin-semantic:

   Binary Strings: binary data (normally not readable by humans) represented
   as a character string.  In Python 3 the main built-in type for this concept
   is `bytes`:class:.

__ https://en.wikipedia.org/wiki/Unicode


Mismatch Semantics Comparison
-----------------------------

In Python 2 series, equal comparison for `unicode` an `str` types don't ever
match.  The following example fails in that version::

  >>> s = 'λ'
  >>> u = u'λ'
  >>> u == s
  False

Also a ``UnicodeWarning`` is issued with message "Unicode equal comparison
failed to convert both arguments to Unicode - interpreting them as being
unequal.

To correctly compare, use the same type.  For example::

  >>> from xoutil.eight.text import force
  >>> force(s) == force(u)
  True


Compatibility Modules
---------------------

**Xoutil** has a Python 2 and 3 compatibility package named
`~xoutil.eight`:mod:.  So these issues related to ambiguity when handling
strings (see `Text versus binary data`__) are dealt in the sub-modules:

- `~xoutil.eight.text`:mod:\ : tools related with `text handling
  <text-semantic_>`__.  In Python 2 values are processed with `unicode`_ and
  in Python 3 with standard `str`:class: type.

- `~xoutil.eight.string`:mod:\ : tools that in both versions of Python always
  use standard `str`:class: type to fulfills `technical strings semantics
  <tech-semantic_>`__.

__ https://docs.python.org/3/howto/pyporting.html#text-versus-binary-data

These modules can be used transparently in both Python versions.


Encoding Hell
-------------

To represent a entire range of characters is used some kind of `encoding
system`__.  Maybe the trending top is the `UTF (Unicode Transformation
Format)`:abbr: family.

__ https://en.wikipedia.org/wiki/Character_encoding

This complex diversity, even when strictly necessary for most applications,
represents an actual "hell" for programmers.

For more references see `codecs`:mod: standard module.  Also the
`xoutil.future.codecs`:mod:, and `xoutil.eight.text`:mod: extension modules.

.. Local document hyper-links

.. _unicode: https://docs.python.org/2/library/functions.html#unicode



.. |xoutil-string-1_8| replace:: Changes in 1.8.0 in `xoutil.string`:mod:.
.. _xoutil-string-1_8:

|xoutil-string-1_8|
-------------------

- `xoutil.future.codecs`:mod:\ : Moved here functions
  `~xoutil.future.codecs.force_encoding`:func:,
  `~xoutil.future.codecs.safe_decode`:func:, and
  `~xoutil.future.codecs.safe_encode`:func:.

- `xoutil.eight.string`:mod:\ : Technical string handling.  In this module:

  - `~xoutil.eight.string.force`:func:\ : Replaces old ``safe_str``, and
    ``force_str`` versions.

  - `~xoutil.eight.string.safe_join`:func:\ : Replaces old version in
    ``future`` module.  This function is useless, it's equivalent to::

      force(vale).join(force(item) for item in iterator)

  - `~xoutil.eight.string.force_ascii`:func:\ : Replaces old
    ``normalize_ascii``.   This function is safe and the result will be of
    standard ``str`` type containing only equivalent ASCII characters from
    the argument.

- `xoutil.eight.text`:mod:\ : Text handling, strings can be part of
  internationalization processes.  In this module:

  - `~xoutil.eight.text.force`:func:\ : Replaces old ``safe_str``, and
    ``force_str`` versions, but always returning the text type.

  - `~xoutil.eight.text.safe_join`:func:\ : Replaces old version in
    ``future`` module, but in this case always return the text type.  This
    function is useless, it's equivalent to::

      force(vale).join(force(item) for item in iterator)

- ``capitalize_word`` function was completely removed, use instead standard
  method ``word.capitalize()``.

- Functions ``capitalize``, ``normalize_name``, ``normalize_title``,
  ``normalize_str``, ``parse_boolean``, ``parse_url_int`` were completely
  removed.

- ``normalize_unicode`` was completely removed, it's now replaced by
  `xoutil.eight.text.force`:func:.

- ``hyphen_name`` was moved to `xoutil.cli.tools`:mod:.

- ``strfnumber`` was moved as an internal function of
  'xoutil.future.datetime':mod: module.

- Function ``normalize_slug`` is now deprecated.  You should use now
  `~xoutil.string.slugify`:func:\ .
