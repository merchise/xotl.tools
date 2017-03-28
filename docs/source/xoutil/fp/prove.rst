`xoutil.fp.prove`:mod: - Prove validity of values
=================================================

.. module:: xoutil.fp.prove

.. sectionauthor:: Medardo Rodriguez <med@merchise.org>

--------------

There is an amalgam of methods to manage "safe functions": those that all
fails are homogenized.

A predicate (that which is affirmed or denied of a thing) are very difficult to
manage in a safe way, bacause of that : return a Boolean indicating if a value is valid or not.  In the
diversity of programming languages there is special values:

  - In Haskell: The ``Maybe`` datatype provides a way to make a safety wrapper
    around functions which can fail to work for a range of arguments.

  - In Lisp: ``t`` and ``nil`` are the equivalent for ``True`` and ``False``.

- Exception handling: In most languages there are structures to manage
  execeptions.


The idea that proofs are programs has had a long history.  The situation is
currently that proof-checkers have been implemented for a range of
type-theories that are at the same time type-checkers for a dependently typed
functional programming language.

.. autofunction:: vouch

.. autoclass:: Coercer
