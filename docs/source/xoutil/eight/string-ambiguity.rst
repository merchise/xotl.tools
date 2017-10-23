:orphan:

.. |py-string-ambiguity| replace:: String Ambiguity in Python
.. _py-string-ambiguity:

|py-string-ambiguity|
=====================

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


.. [#] Or migrated to `~xoutil.eight`:mod: sub-modules.
