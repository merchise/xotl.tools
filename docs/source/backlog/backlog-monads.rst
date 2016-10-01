Integrate several current modules into ``xoutil.monads``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


There are several "old" modules that could be migrated (integrated) into
`xoutil.monads`:mod:; also these old modules could become clients of Monads.

- `~xoutil.connote`:mod:\ : Intends for to have predicates (commonly
  understood to be Boolean-valued functions).

- `~xoutil.symbols`:mod:\ : instance and sub-class checks in `MetaSymbol` must
  be extended to be compliant with monads.

- `~xoutil.cl`:mod:\ : Reproducing some concepts of "Common Lisp" in Pythond.
  The checkers (coercers) are the best candidates to be monadic.

- `~xoutil.values`:mod:\ : This module is deprecated but must be analyzed in
  this proccess.
