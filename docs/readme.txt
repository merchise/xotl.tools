`xoutil` is a collection of disparate utilities that does not conform a
framework for anything.  `xoutil` is essentially an extension to the Python's
standard library.

xoutil provides a basic implementation of :mod:`execution contexts
<xoutil.context>`, that allows a programmer to enter/exit an execution
context; which then may signal a component to behave differently.  This
implementation of contexts does not support distribution, though.  But it's
useful to implement components that have two different interfaces according to
the context in which they are invoked.  In this regard, contexts are a thin
(but very idiomatic) alternative to some of the design patterns found
elsewhere.
