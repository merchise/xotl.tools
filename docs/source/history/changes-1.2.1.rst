- Loads for improvements for Python 3k compatibility: Several modules were
  fixed or adapted to work on both Python 2.7 and Python 3.2. They include (but
  we might have forgotten some):

  - :mod:`xoutil.context`
  - :mod:`xoutil.aop.basic`
  - :mod:`xoutil.deprecation`
  - :mod:`xoutil.proxy`

- Rescues :mod:`xoutil.annotate` and is going to be supported from
  now on.

- Introduces module :mod:`xoutil.subprocess` and function
  :func:`xoutil.subprocess.call_and_check_output`.

- Introduces module :mod:`xoutil.decorator.compat` that enables constructions
  that are interoperable in Python 2 and Python 3.

- Introduces :func:`xoutil.iterators.izip` since it was removed from Python 3k
  standard library.

..  LocalWords:  xoutil
