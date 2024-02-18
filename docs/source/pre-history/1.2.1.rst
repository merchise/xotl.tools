- Loads of improvements for Python 3k compatibility: Several modules were
  fixed or adapted to work on both Python 2.7 and Python 3.2. They include (but
  we might have forgotten some):

  - ``xoutil.context``
  - ``xoutil.aop.basic``
  - ``xoutil.deprecation``
  - ``xoutil.proxy``

- Rescued ``xoutil.annotate`` and is going to be supported from
  now on.

- Introduced module ``xoutil.subprocess`` and function
  ``xoutil.subprocess.call_and_check_output``.

- Introduced module ``xoutil.decorator.compat`` that enables constructions
  that are interoperable in Python 2 and Python 3.

- Introduced ``xoutil.iterators.zip``, ``xoutil.iterators.izip``,
  ``xoutil.iterators.map``, and ``xoutil.iterators.imap``.


..  LocalWords:  xoutil
