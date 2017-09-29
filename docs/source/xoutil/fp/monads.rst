``xoutil.fp.monads`` - Some simple and experimental monads
==========================================================

.. automodule:: xoutil.fp.monads


Some thoughts about this package
--------------------------------

In pure *functional programming*, a monad is used to represent computations
that requires sequenced operations, or to define arbitrary deterministic
control flows (like handling concurrency, continuations, or exceptions).

See `Monads in functional programming`__ for more information.

__ http://en.wikipedia.org/wiki/Monads_in_functional_programming

But in Python (at least for me), Monads are a way to homogenize *functional
programming* concepts with a simple syntax in order to code becomes easier to
understand.  If you'd find the full-power of *Monads*, go to *Haskell*, or
maybe to *Category Theory* in mathematics.


Contents
--------

.. toctree::
   :maxdepth: 1
   :glob:

   monads/*
